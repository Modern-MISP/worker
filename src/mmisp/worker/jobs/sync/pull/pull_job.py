import asyncio
from uuid import UUID

from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxy_clusters import GetGalaxyClusterResponse, SearchGalaxyClusterGalaxyClustersDetails
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.shadow_attribute import ShadowAttribute
from mmisp.api_schemas.sharing_groups import (
    GetAllSharingGroupsResponseResponseItem,
    GetAllSharingGroupsResponseResponseItemSharingGroupOrgItem,
    GetAllSharingGroupsResponseResponseItemSharingGroupServerItem,
)
from mmisp.api_schemas.sightings import SightingAttributesResponse
from mmisp.db.database import sessionmanager
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import InvalidAPIResponse, APIException
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.jobs.sync.sync_helper import _get_mini_events_from_server
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import filter_blocked_clusters, get_server
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser

JOB_NAME = "pull_job"
__logger = get_task_logger(JOB_NAME)

# TODO: Remove after debugging or implement env variable
__logger.setLevel("DEBUG")


@celery_app.task
def pull_job(user_data: UserData, pull_data: PullData) -> PullResult:
    """
    This function represents the pull job. It pulls data from a remote server and saves it in the local server.
    :param user_data: The user data of the user who started the job.
    :param pull_data: The data needed to pull the data from the remote server.
    :return: An object containing the results of the pull job.
    """
    return asyncio.run(_pull_job(user_data, pull_data))


async def _pull_job(user_data: UserData, pull_data: PullData) -> PullResult:
    sync_config: SyncConfigData = sync_config_data
    async with sessionmanager.session() as session:
        misp_api = MispAPI(session)
        server_id: int = pull_data.server_id
        technique: PullTechniqueEnum = pull_data.technique
        remote_server: Server | None = await get_server(session, server_id)
        if remote_server is None:
            raise JobException(f"Remote server with id {server_id} not found.")

        if not remote_server.pull:
            raise ForbiddenByServerSettings(f"Pulling from Server with id {remote_server.id} is not allowed.")

        user: MispUser = await misp_api.get_user(user_data.user_id)
        pulled_clusters: int = 0
        if remote_server.pull_galaxy_clusters:
            pulled_clusters = await __pull_clusters(session, misp_api, user, technique, remote_server)
            __logger.info(f"{pulled_clusters} galaxy clusters pulled or updated.")

        if technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
            return PullResult(
                successes=0, fails=0, pulled_proposals=0, pulled_sightings=0, pulled_clusters=pulled_clusters
            )

        pull_event_return: tuple[int, int] = await __pull_events(
            session, misp_api, sync_config, user, technique, remote_server
        )
        pulled_events: int = pull_event_return[0]
        failed_pulled_events: int = pull_event_return[1]
        __logger.info(f"{pulled_events} events pulled or updated.")
        __logger.info(f"{failed_pulled_events} events failed or didn't need an update.")

        pulled_proposals: int = 0
        pulled_sightings: int = 0
        if technique == PullTechniqueEnum.FULL or technique == PullTechniqueEnum.INCREMENTAL:
            pulled_proposals = await __pull_proposals(misp_api, user, remote_server)
            __logger.info(f"{pulled_proposals} proposals pulled or updated.")
            pulled_sightings = await __pull_sightings(misp_api, remote_server)
            __logger.info(f"{pulled_sightings} sightings pulled or updated.")
        return PullResult(
            successes=pulled_events,
            fails=failed_pulled_events,
            pulled_proposals=pulled_proposals,
            pulled_sightings=pulled_sightings,
            pulled_clusters=pulled_clusters,
        )


# Functions designed to help with the Galaxy Cluster push ----------->


async def __pull_clusters(
        session: AsyncSession, misp_api: MispAPI, user: MispUser, technique: PullTechniqueEnum, remote_server: Server
) -> int:
    """
    This function pulls the galaxy clusters from the remote server and saves them in the local server.
    :param user: The user who started the job.
    :param technique: The technique used to pull the galaxy clusters.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: The number of pulled galaxy clusters.
    """

    pulled_clusters: int = 0
    cluster_ids: list[int] = await __get_cluster_id_list_based_on_pull_technique(
        session, misp_api, user, technique, remote_server
    )

    for cluster_id in cluster_ids:
        try:
            cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster_id, remote_server)
            if misp_api.save_cluster(cluster):
                pulled_clusters += 1
            else:
                __logger.info(f"Cluster with id {cluster_id} already exists and is up to date.")
        except Exception as e:
            __logger.warning(
                f"Error while pulling galaxy cluster with id {cluster_id}, "
                f"from Server with id {remote_server.id}: " + str(e)
            )
    return pulled_clusters


async def __get_cluster_id_list_based_on_pull_technique(
        session: AsyncSession, misp_api: MispAPI, user: MispUser, technique: PullTechniqueEnum, remote_server: Server
) -> list[int]:
    """
    This function returns a list of galaxy cluster ids based on the pull technique.
    :param user: The user who started the job.
    :param technique: The technique used to pull the galaxy clusters.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster ids.
    """
    if technique == PullTechniqueEnum.INCREMENTAL or technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return await __get_local_cluster_ids_from_server_for_pull(session, misp_api, user, remote_server)
    else:
        return await __get_all_cluster_ids_from_server_for_pull(session, misp_api, user, remote_server)


async def __get_local_cluster_ids_from_server_for_pull(
        session: AsyncSession, misp_api: MispAPI, user: MispUser, remote_server: Server
) -> list[int]:
    """
    This function returns a list of galaxy cluster ids, from the locale server, based on the pull technique.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster ids.
    """

    local_galaxy_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await __get_accessible_local_cluster(
        misp_api, user)
    if len(local_galaxy_clusters) == 0:
        return []
    conditions: dict = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(conditions,
                                                                                                         remote_server)
    local_id_dic: dict[int, SearchGalaxyClusterGalaxyClustersDetails] = {cluster.id: cluster for cluster in
                                                                         local_galaxy_clusters}
    remote_clusters = __get_intersection(local_id_dic, remote_clusters)
    remote_clusters = await filter_blocked_clusters(session, remote_clusters)
    out: list[int] = []
    for cluster in remote_clusters:
        if local_id_dic[cluster.id].version < cluster.version:
            out.append(cluster.id)
    return out


async def __get_all_cluster_ids_from_server_for_pull(
        session: AsyncSession, misp_api: MispAPI, user: MispUser, remote_server: Server
) -> list[int]:
    """
    This function returns a list of galaxy cluster ids, from the remote server, based on the pull technique.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster ids.
    """

    conditions: dict = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(conditions,
                                                                                                         remote_server)
    remote_clusters = await filter_blocked_clusters(session, remote_clusters)

    local_galaxy_clusters: list[GetGalaxyClusterResponse] = await __get_all_clusters_with_id(
        misp_api, [cluster.id for cluster in remote_clusters]
    )
    local_id_dic: dict[int, GetGalaxyClusterResponse] = {cluster.id: cluster for cluster in local_galaxy_clusters}
    out: list[int] = []
    for cluster in remote_clusters:
        if local_id_dic[cluster.id].version < cluster.version:
            out.append(cluster.id)
    return out


async def __get_accessible_local_cluster(misp_api: MispAPI, user: MispUser) -> list[
    SearchGalaxyClusterGalaxyClustersDetails]:
    """
    This function returns a list of galaxy clusters that the user has access to.
    :param user: The user who started the job.
    :return: A list of galaxy clusters.
    """

    conditions: dict = {"published": True, "minimal": True, "custom": True}
    local_galaxy_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(
        conditions)

    if not user.role.perm_site_admin:
        sharing_ids: list[int] = await __get_sharing_group_ids_of_user(misp_api, user)
        out: list[SearchGalaxyClusterGalaxyClustersDetails] = []
        for cluster in local_galaxy_clusters:
            if (
                    cluster.org_id == user.org_id
                    and 0 < int(cluster.distribution) < 4
                    and cluster.sharing_group_id in sharing_ids
            ):
                out.append(cluster)
        return out

    return local_galaxy_clusters


async def __get_all_clusters_with_id(misp_api: MispAPI, ids: list[int]) -> list[GetGalaxyClusterResponse]:
    """
    This function returns a list of galaxy clusters with the given ids.
    :param ids: The ids of the galaxy clusters.
    :return: A list of galaxy clusters.
    """
    out: list[GetGalaxyClusterResponse] = []
    for cluster_id in ids:
        try:
            out.append(await misp_api.get_galaxy_cluster(cluster_id))
        except Exception as e:
            __logger.warning(f"Error while getting galaxy cluster, with id {cluster_id}, from own Server: " + str(e))

    return out


async def __get_sharing_group_ids_of_user(misp_api: MispAPI, user: MispUser) -> list[int]:
    """
    This function returns a list of sharing group ids that the user has access to.
    :param user: The user who started the job.
    :return: A list of sharing group ids.
    """

    sharing_groups: list[GetAllSharingGroupsResponseResponseItem] = await misp_api.get_sharing_groups()
    if user.role.perm_site_admin:
        return [int(sharing_group.SharingGroup.id) for sharing_group in sharing_groups]

    out: list[int] = []
    for sharing_group in sharing_groups:
        if sharing_group.Organisation.id == user.org_id:
            sharing_group_servers: list[GetAllSharingGroupsResponseResponseItemSharingGroupServerItem] = (
                sharing_group.SharingGroupServer
            )
            sharing_group_orgs: list[GetAllSharingGroupsResponseResponseItemSharingGroupOrgItem] = (
                sharing_group.SharingGroupOrg
            )
            for sharing_group_server in sharing_group_servers:
                if (sharing_group_server.all_orgs and sharing_group_server.server_id == "0") or any(
                        sharing_group_org.org_id == user.org_id for sharing_group_org in sharing_group_orgs
                ):
                    out.append(int(sharing_group.SharingGroup.id))
                    break
    return out


# <-----------

# Functions designed to help with the Event pull ----------->


async def __pull_events(
        session: AsyncSession,
        misp_api: MispAPI,
        sync_config: SyncConfigData,
        user: MispUser,
        technique: PullTechniqueEnum,
        remote_server: Server,
) -> tuple[int, int]:
    """
    This function pulls the events from the remote server and saves them in the local server.
    :param user: The user who started the job.
    :param technique: The technique used to pull the events.
    :param remote_server: The remote server from which the events are pulled.
    :return: The number of pulled events and the number of failed pulled events.
    """

    pulled_events: int = 0
    remote_event_ids: list[int] = await __get_event_ids_based_on_pull_technique(
        session, misp_api, sync_config, technique, remote_server
    )
    for event_id in remote_event_ids:
        if await __pull_event(misp_api, event_id, remote_server):
            pulled_events += 1
        else:
            __logger.info(f"Event with id {event_id} already exists and is up to date.")
    failed_pulled_events: int = len(remote_event_ids) - pulled_events
    return pulled_events, failed_pulled_events


async def __get_event_ids_based_on_pull_technique(
        session: AsyncSession,
        misp_api: MispAPI,
        sync_config: SyncConfigData,
        technique: PullTechniqueEnum,
        remote_server: Server,
) -> list[int]:
    """
    This function returns a list of event ids based on the pull technique.
    :param technique: The technique used to pull the events.
    :param remote_server: The remote server from which the events are pulled.
    :return: A list of event ids.
    """
    local_minimal_events: list[MispMinimalEvent] = await misp_api.get_minimal_events(True)
    local_event_ids: list[int] = [event.id for event in local_minimal_events]
    if technique == PullTechniqueEnum.FULL:
        return await __get_event_ids_from_server(session, misp_api, sync_config, False, local_event_ids, remote_server)
    elif technique == PullTechniqueEnum.INCREMENTAL:
        remote_event_ids: list[int] = await __get_event_ids_from_server(
            session, misp_api, sync_config, True, local_event_ids, remote_server
        )
        # TODO: This is not "incremental"
        return list(set(local_event_ids) & set(remote_event_ids))
    else:
        return []


async def __pull_event(misp_api: MispAPI, event_id: int, remote_server: Server) -> bool:
    """
    This function pulls the event from the remote server and saves it in the local server.
    :param event_id: The id of the event.
    :param remote_server: The remote server from which the event is pulled.
    :return: True if the event was pulled successfully, False otherwise.
    """

    try:
        event: AddEditGetEventDetails = await misp_api.get_event(event_id, remote_server)
    except (APIException, InvalidAPIResponse) as e:
        __logger.warning(
            f"Error while fetching Event with id {event_id} from Server with id {remote_server.id}: " + str(e)
        )
        return False

    if await misp_api.save_event(event):
        __logger.debug(f"Event {event.uuid} saved locally. Pulled from Server {remote_server.id}.")
        return True
    else:
        if await misp_api.update_event(event):
            __logger.debug(f"Event {event.uuid} updated. Update pulled from Server {remote_server.id}.")
            return True
        else:
            __logger.warning(
                f"Error while pulling Event with id {event_id} from Server with id {remote_server.id}. "
                f"Event should exist locally but cannot be updated."
            )

    return False


async def __get_event_ids_from_server(
        session: AsyncSession,
        misp_api: MispAPI,
        sync_config: SyncConfigData,
        ignore_filter_rules: bool,
        local_event_ids: list[int],
        remote_server: Server,
) -> list[int]:
    """
    This function returns a list of event ids from the remote server.
    :param ignore_filter_rules: If True, the filter rules will be ignored. If False, the filter rules will be applied.
    :param local_event_ids: The ids of the events that are saved in the local server.
    :param remote_server: The remote server from which the event ids are pulled.
    :return: A list of event ids.
    """
    remote_event_views: list[MispMinimalEvent] = await _get_mini_events_from_server(
        session,
        ignore_filter_rules,
        local_event_ids,
        sync_config,
        misp_api,
        remote_server,
    )

    return [event.id for event in remote_event_views]


# <-----------


# Functions designed to help with the Proposal pull ----------->
async def __pull_proposals(misp_api: MispAPI, user: MispUser, remote_server: Server) -> int:
    """
    This function pulls the proposals from the remote server and saves them in the local server.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the proposals are pulled.
    :return: The number of pulled proposals.
    """
    fetched_proposals: list[ShadowAttribute] = await misp_api.get_proposals(remote_server)
    pulled_proposals: int = 0
    for proposal in fetched_proposals:
        try:
            event: AddEditGetEventDetails = await misp_api.get_event(UUID(proposal.event_uuid), remote_server)
            if await misp_api.save_proposal(event):
                pulled_proposals += 1
            else:
                __logger.info(f"Proposal with id {proposal.id} already exists and is up to date.")
        except Exception as e:
            __logger.warning(
                f"Error while pulling Event with id {proposal.event_id}, "
                f"from Server with id {remote_server.id}: " + str(e)
            )
    return pulled_proposals


# <-----------
# Functions designed to help with the Sighting pull ----------->


async def __pull_sightings(misp_api: MispAPI, remote_server: Server) -> int:
    """
    This function pulls the sightings from the remote server and saves them in the local server.
    :param remote_server: The remote server from which the sightings are pulled.
    :return: The number of pulled sightings.
    """

    remote_event_views: list[MispMinimalEvent] = await misp_api.get_minimal_events(False, remote_server)

    local_event_views: list[MispMinimalEvent] = await misp_api.get_minimal_events(True)
    local_event_ids_dic: dict[int, MispMinimalEvent] = {event.id: event for event in local_event_views}

    event_ids: list[int] = []
    for remote_event in remote_event_views:
        if remote_event.id in local_event_ids_dic and remote_event.timestamp > int(
                local_event_ids_dic[remote_event.id].timestamp
        ):
            event_ids.append(remote_event.id)

    fetched_sightings: list[SightingAttributesResponse] = []
    for event_id in event_ids:
        try:
            fetched_sightings.extend(await misp_api.get_sightings_from_event(event_id, remote_server))
        except Exception as e:
            __logger.warning(
                f"Error while pulling Sightings from Event with id {event_id}, "
                f"from Server with id {remote_server.id}: " + str(e)
            )

    pulled_sightings: int = 0
    for sighting in fetched_sightings:
        if misp_api.save_sighting(sighting):
            pulled_sightings += 1
        else:
            __logger.info(f"Sighting with id {sighting.id} already exists and is up to date.")
    return pulled_sightings


# <-----------

# Helper functions ----------->


def __get_intersection(
        cluster_dic: dict[int, SearchGalaxyClusterGalaxyClustersDetails],
        cluster_list: list[SearchGalaxyClusterGalaxyClustersDetails]
) -> list[SearchGalaxyClusterGalaxyClustersDetails]:
    """
    This function returns the intersection of the cluster_dic and the cluster_list.
    :param cluster_dic: A dictionary containing the galaxy clusters.
    :param cluster_list: A list containing the galaxy clusters.
    :return: A list containing the intersection of the cluster_dic and the cluster_list.
    """
    out: list[SearchGalaxyClusterGalaxyClustersDetails] = []
    for cluster in cluster_list:
        for local_cluster_id in cluster_dic:
            if cluster.id == local_cluster_id:
                out.append(cluster)
    return out

# <-----------
