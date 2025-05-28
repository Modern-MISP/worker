import json
import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession
from streaq import WrappedContext

from mmisp.api_schemas.events import AddEditGetEventDetails, AddEditGetEventTag
from mmisp.api_schemas.galaxy_clusters import (
    GalaxyClusterSearchBody,
    PutGalaxyClusterRequest,
    SearchGalaxyClusterGalaxyClustersDetails,
)
from mmisp.api_schemas.server import ServerVersion
from mmisp.api_schemas.sharing_groups import GetAllSharingGroupsResponseResponseItem
from mmisp.api_schemas.sightings import SightingAttributesResponse
from mmisp.db.database import sessionmanager
from mmisp.db.models.server import Server as db_Server
from mmisp.lib.distribution import EventDistributionLevels
from mmisp.lib.logger import alog
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings
from mmisp.worker.jobs.sync.push.job_data import PushData, PushResult, PushTechniqueEnum
from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.jobs.sync.sync_helper import _get_mini_events_from_server
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import get_server, set_last_pushed_id
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent

from ..queue import queue

JOB_NAME = "pull_job"
__logger = logging.getLogger("mmisp")


@queue.task()
async def push_job(ctx: WrappedContext[None], user_data: UserData, push_data: PushData) -> PushResult:
    """
    This function represents the push job. It pushes the data to the remote server.
    :param user_data: The user data of the user that started the job.
    :param push_data: The push data that contains the server id and the technique.
    :return: The result of the push job.
    """
    sync_config: SyncConfigData = sync_config_data
    assert sessionmanager is not None

    async with sessionmanager.session() as session:
        misp_api = MispAPI(session)
        server_id: int = push_data.server_id
        technique: PushTechniqueEnum = push_data.technique

        remote_server: db_Server | None = await get_server(session, server_id)

        if remote_server is None:
            raise JobException(f"Remote server with id {server_id} not found.")

        if not remote_server.push:
            raise ForbiddenByServerSettings("Remote server does not allow push.")

        server_version: ServerVersion = await misp_api.get_server_version(remote_server)

        if not server_version.perm_sync and not server_version.perm_sighting:
            raise ForbiddenByServerSettings("Remote instance is outdated.")

        # check whether server allows push
        local_sharing_groups: list[GetAllSharingGroupsResponseResponseItem] = await misp_api.get_sharing_groups()
        if remote_server.push and server_version.perm_sync:
            if remote_server.push_galaxy_clusters:
                await __push_clusters(misp_api, remote_server, None)

            await __push_events(misp_api, technique, local_sharing_groups, server_version, remote_server, session)

            await __push_proposals(misp_api, session, sync_config, remote_server)

        else:
            __logger.warning(
                f"Push to server {remote_server.id} is not allowed: "
                f"push set to {remote_server.push} and perm_sync set to {server_version.perm_sync}"
            )

        # TODO: singhtings implementation is wrong, to be implemented
        """
        if remote_server.push_sightings and server_version.perm_sighting:
            pushed_sightings: int = await __push_sightings(
                misp_api, session, sync_config, sharing_groups, remote_server
            )
            __logger.info(f"Pushed {pushed_sightings} sightings to server {remote_server.id}")
        """
        return PushResult(success=True)


# Functions designed to help with the Galaxy Cluster push ----------->


@alog
async def __push_clusters(
    misp_api: MispAPI, remote_server: db_Server, clusters_to_push: list[SearchGalaxyClusterGalaxyClustersDetails] | None
) -> None:
    """
    This function pushes the given clusters (local_clusters) in to the given remote server.
    :param remote_server: The remote server to push the local_clusters to.
    :param misp_api: The MISP API to use.
    :param clusters_to_push: The clusters to push. If None, local_clusters will be determined by the function.
    :return: The number of local_clusters that were pushed.
    """

    if clusters_to_push is None:
        conditions: GalaxyClusterSearchBody = GalaxyClusterSearchBody(published=True, custom=True)
        local_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(conditions)
    else:
        local_clusters = clusters_to_push

    conditions = GalaxyClusterSearchBody(
        published=True, minimal=True, custom=True, uuid=[cluster.uuid for cluster in local_clusters]
    )
    remote_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(
        conditions, remote_server
    )

    remote_cluster_uuids: list[str] = [cluster.uuid for cluster in remote_clusters]

    local_clusters = await __remove_older_clusters(local_clusters, remote_clusters)
    __logger.debug(
        f"Found {len(local_clusters)} local_clusters to push to server {remote_server.id}. "
        f"{[cluster.uuid for cluster in local_clusters]}"
    )

    pushed_clusters: int = 0

    for cluster in local_clusters:
        if cluster.uuid in remote_cluster_uuids:
            if await misp_api.update_cluster(PutGalaxyClusterRequest(**cluster.model_dump()), remote_server):
                pushed_clusters += 1
            else:
                __logger.info(f"Cluster with id {cluster.id} already exists on server {remote_server.id}.")
        else:
            if await misp_api.save_cluster(cluster, remote_server):
                pushed_clusters += 1
            else:
                __logger.info(f"Cluster with id {cluster.id} already exists on server {remote_server.id}.")

    __logger.info(f"Pushed {pushed_clusters} local_clusters to server {remote_server.id}")


@alog
async def __remove_older_clusters(
    local_clusters: list[SearchGalaxyClusterGalaxyClustersDetails],
    remote_clusters: list[SearchGalaxyClusterGalaxyClustersDetails],
) -> list[SearchGalaxyClusterGalaxyClustersDetails]:
    """
    This function removes the clusters that are older than the ones on the remote server.
    :param local_clusters: The clusters to check.
    :param remote_server: The remote server to check the clusters against.
    :return: The clusters that are not older than the ones on the remote server.
    """
    remote_clusters_dict: dict[str, SearchGalaxyClusterGalaxyClustersDetails] = {
        cluster.uuid: cluster for cluster in remote_clusters
    }
    out: list[SearchGalaxyClusterGalaxyClustersDetails] = []
    for cluster in local_clusters:
        if cluster.uuid not in remote_clusters_dict or int(remote_clusters_dict[cluster.uuid].version) <= int(
            cluster.version
        ):
            out.append(cluster)
    return out


# <----------

# Functions designed to help with the Event push ----------->


@alog
async def __push_events(
    misp_api: MispAPI,
    technique: PushTechniqueEnum,
    local_sharing_groups: list[GetAllSharingGroupsResponseResponseItem],
    server_version: ServerVersion,
    remote_server: db_Server,
    session: AsyncSession,
) -> None:
    """
    This function pushes the events in the local server based on the technique to the remote server.
    :param technique: The technique to use.
    :param local_sharing_groups: The sharing groups of the local server.
    :param server_version: The version of the remote server.
    :param remote_server: The remote server to push the events to.
    :return: The number of events that were pushed.
    """
    server_sharing_group_ids: list[int] = []
    for sharing_group in local_sharing_groups:
        if not __server_in_sg(sharing_group, remote_server):
            server_sharing_group_ids.append(sharing_group.SharingGroup.id)

    local_events: list[AddEditGetEventDetails] = await __get_local_event_views(
        misp_api, server_sharing_group_ids, technique, remote_server
    )

    # await misp_api.filter_events_for_push(local_events, remote_server)
    pushed_events: int = 0
    highes_event_id: int = 0

    for event in local_events:
        # Removes mypy error. event.id should never be None.
        if not event.id:
            __logger.warning(f"Event with uuid {event.uuid} has no local id. Cannot be pushed.")
            continue

        if event.distribution == EventDistributionLevels.CONNECTED_COMMUNITIES:
            event.distribution = EventDistributionLevels.COMMUNITY

        if await __push_event(misp_api, event, server_version, technique, remote_server):
            pushed_events += 1
            if event.id > highes_event_id:
                highes_event_id = event.id
        else:
            __logger.info(
                f"Event with id {event.id} and uuid {event.uuid} already exists on server {remote_server.id} "
                f"and is up to date."
            )

    __logger.info(f"_push_job: Pushed {pushed_events} events to server {remote_server.id}")

    await set_last_pushed_id(session, int(str(remote_server.id)), highes_event_id)


@alog
async def __get_local_event_views(
    misp_api: MispAPI, server_sharing_group_ids: list[int], technique: PushTechniqueEnum, server: db_Server
) -> list[AddEditGetEventDetails]:
    local_mini_events: list[MispMinimalEvent] = await misp_api.get_minimal_events(ignore_filter_rules=True)

    filtered_events = []

    if technique == PushTechniqueEnum.INCREMENTAL:
        for mini_event in local_mini_events:
            if mini_event.id > server.last_pushed_id:
                filtered_events.append(mini_event)
            else:
                __logger.debug(
                    f"Incremental_push_job: Event with id {mini_event.id} and uuid {mini_event.uuid} is not allowed "
                    f"to be pushed to server {server.id} because it is event_id is not greater than the last_pushed_id"
                )
    else:
        filtered_events = local_mini_events

    local_events: list[AddEditGetEventDetails] = []
    for event_view in filtered_events:
        try:
            event: AddEditGetEventDetails = await misp_api.get_event(event_view.id)
            local_events.append(event)
        except Exception as e:
            __logger.warning(
                f"__get_local_event_views: Could not get event with id: {event_view.id} and "
                f"uuid: {event_view.uuid} from server {server.id}: {e}"
            )

    out: list[AddEditGetEventDetails] = []
    for event in local_events:
        if (
            event.published
            and len(event.Attribute) > 0
            and 0 < event.distribution < 4
            or event.distribution == 4
            and event.sharing_group_id in server_sharing_group_ids
        ):
            out.append(event)
        else:
            __logger.debug(
                f"Event with id {event.id} is not allowed to be pushed to server {server.id}."
                f" Distribution: {event.distribution}, Sharing Group: {event.sharing_group_id}"
                f" Published: {event.published}, Attributes: {len(event.Attribute)}"
            )

    return out


@alog
async def __push_event(
    misp_api: MispAPI,
    event: AddEditGetEventDetails,
    server_version: ServerVersion,
    technique: PushTechniqueEnum,
    server: db_Server,
) -> bool:
    """
    This function pushes the event with the given id to the remote server. It also pushes the clusters if the server
    and technique allows it.
    :param event: The event to push.
    :param server_version: The version of the remote server.
    :param technique: The technique to use.
    :param server: The remote server.
    :return: Whether the event was pushed.
    """

    if server_version.perm_galaxy_editor and server.push_galaxy_clusters and technique == PushTechniqueEnum.FULL:
        await __push_event_cluster_to_server(misp_api, event, server)

    if not await misp_api.save_event(event, server):
        return await misp_api.update_event(event, server)
    return True


@alog
async def __push_event_cluster_to_server(misp_api: MispAPI, event: AddEditGetEventDetails, server: db_Server) -> None:
    """
    This function pushes the clusters of the event to the remote server.
    :param event: The event to push the clusters of.
    :param server: The remote server.
    :return: The number of clusters that were pushed.
    """
    tags: list[AddEditGetEventTag] = event.Tag
    tag_names: list[str] = [tag.name for tag in tags]
    custom_cluster_tagnames: list[str] = list(filter(__is_custom_cluster_tag, tag_names))

    conditions: GalaxyClusterSearchBody = GalaxyClusterSearchBody(published=True, custom=True)
    all_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(conditions)

    clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = []
    for cluster in all_clusters:
        if cluster.tag_name in custom_cluster_tagnames:
            clusters.append(cluster)

    await __push_clusters(misp_api, server, clusters)


def __is_custom_cluster_tag(tag: str) -> bool:
    """
    This function checks whether the tag is a custom galaxy-cluster tag.
    :param tag: The tag to check.
    :return: Whether the tag is a custom galaxy-cluster tag.
    """
    regex: str = '/misp-galaxy:[^:="]+="[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"/i'
    return re.match(regex, tag) is not None


# <----------


# Functions designed to help with the Proposal push ----------->
@alog
async def __push_proposals(
    misp_api: MispAPI, session: AsyncSession, sync_config: SyncConfigData, remote_server: db_Server
) -> None:
    """
    This function pushes the proposals in the local server to the remote server.
    :param remote_server: The remote server to push the proposals to.
    :return: The number of proposals that were pushed.
    """
    local_event_views: list[MispMinimalEvent] = await misp_api.get_minimal_events(True)
    local_event_ids: list[int] = [event.id for event in local_event_views]
    event_views: list[MispMinimalEvent] = await _get_mini_events_from_server(
        session, True, local_event_ids, sync_config, misp_api, remote_server
    )
    pushed_proposals: int = 0
    for event_view in event_views:
        try:
            event: AddEditGetEventDetails = await misp_api.get_event(event_view.id, remote_server)
            if await misp_api.save_proposal(event, remote_server):
                pushed_proposals += 1
            else:
                __logger.info(f"Proposal for event with id {event.id} already exists on server {remote_server.id}.")
        except Exception as e:
            __logger.warning(
                f"__push_proposals_method: Could not get event with id: {event_view.id} and "
                f"uuid: {event_view.uuid} from server {remote_server.id}: {e}"
            )

    __logger.info(f"Pushed {pushed_proposals} proposals to server {remote_server.id}")


# <----------

# Functions designed to help with the Sighting push ----------->


# TODO: sightings implementation is wrong, to be implemented
@alog
async def __push_sightings(
    misp_api: MispAPI,
    session: AsyncSession,
    sync_config: SyncConfigData,
    sharing_groups: list[GetAllSharingGroupsResponseResponseItem],
    remote_server: db_Server,
) -> int:
    """
    This function pushes the sightings in the local server to the remote server.
    :param sharing_groups: The sharing groups of the local server.
    :param remote_server: The remote server to push the sightings to.
    :return: The number of sightings that were pushed.
    """
    remote_event_views: list[MispMinimalEvent] = await _get_mini_events_from_server(
        session, True, [], sync_config, misp_api, remote_server
    )
    local_event_views: list[MispMinimalEvent] = await misp_api.get_minimal_events(True)
    local_event_views_dic: dict[int, MispMinimalEvent] = {event_view.id: event_view for event_view in local_event_views}

    target_event_ids: list[int] = []
    for remote_event_view in remote_event_views:
        event_id: int = remote_event_view.id
        if (
            event_id in local_event_views_dic
            and local_event_views_dic[event_id].timestamp > remote_event_view.timestamp
        ):
            target_event_ids.append(event_id)

    success: int = 0
    for event_id in target_event_ids:
        try:
            event: AddEditGetEventDetails = await misp_api.get_event(event_id)
        except Exception as e:
            __logger.warning(f"__push_sightings: Could not get event {event_id} from server {remote_server.id}: {e}")
            continue
        if not __allowed_by_push_rules(event, remote_server):
            continue
        if not __allowed_by_distribution(sync_config, event, sharing_groups, remote_server):
            continue

        remote_sightings: set[SightingAttributesResponse] = set(
            await misp_api.get_sightings_from_event(event_id, remote_server)
        )
        local_sightings: set[SightingAttributesResponse] = set(await misp_api.get_sightings_from_event(event_id))
        new_sightings: list[SightingAttributesResponse] = list()
        for local_sighting in local_sightings:
            if local_sighting.id not in remote_sightings:
                new_sightings.append(local_sighting)

        if len(new_sightings) == 0:
            continue

        for sighting in new_sightings:
            if await misp_api.save_sighting(sighting, remote_server):
                success += 1
            else:
                __logger.info(f"Sighting with id {sighting.id} already exists on server {remote_server.id}.")
    return success


def __allowed_by_push_rules(event: AddEditGetEventDetails, server: db_Server) -> bool:
    """
    This function checks whether the push of the event-sightings is allowed by the push rules of the remote server.
    :param event: The event to check.
    :param server: The remote server.
    :return: Whether the event-sightings are allowed by the push rules of the remote server.
    """
    push_rules: dict = json.loads(server.push_rules)
    if "tag" in push_rules and event.Tag is not None:
        tags: set[str] = {str(tag) for tag in event.Tag}
        if "OR" in push_rules["tag"]:
            if len(set(push_rules["tag"]["OR"]) & tags) == 0:
                return False

        if "NOT" in push_rules["tag"]:
            if len(set(push_rules["tag"]["NOT"]) & tags) != 0:
                return False

    if "orgs" in push_rules and "OR" in push_rules["orgs"]:
        if len(set(push_rules["orgs"]["OR"]) & {event.orgc_id}) == 0:
            return False

    if "orgs" in push_rules and "NOT" in push_rules["orgs"]:
        if len(set(push_rules["tag"]["NOT"]) & {event.orgc_id}) != 0:
            return False
    return True


def __allowed_by_distribution(
    sync_config: SyncConfigData,
    event: AddEditGetEventDetails,
    sharing_groups: list[GetAllSharingGroupsResponseResponseItem],
    server: db_Server,
) -> bool:
    """
    This function checks whether the push of the event-sightings is allowed by the distribution of the event.
    :param event: The event to check.
    :param sharing_groups: The sharing groups of the local server.
    :param server: The remote server.
    :return: Whether the event-sightings are allowed by the distribution of the event.
    """
    if not server.internal or sync_config.misp_host_org_id != server.remote_org_id:
        if event.distribution < 2:
            return False
    if event.distribution == 4:
        if event.sharing_group_id is not None:
            sharing_group: GetAllSharingGroupsResponseResponseItem | None = __get_sharing_group(
                event.sharing_group_id, sharing_groups
            )
        else:
            sharing_group = None
        if sharing_group is None:
            return False
        return __server_in_sg(sharing_group, server)
    return False


def __get_sharing_group(
    sharing_group_id: int, sharing_groups: list[GetAllSharingGroupsResponseResponseItem]
) -> GetAllSharingGroupsResponseResponseItem | None:
    """
    This function gets the sharing group with the given id from the list of sharing groups.
    :param sharing_group_id: The id of the sharing group to get.
    :param sharing_groups: The list of sharing groups to get the sharing group from.
    :return: The sharing group with the given id.
    """
    for sharing_group in sharing_groups:
        if sharing_group.SharingGroup.id == sharing_group_id:
            return sharing_group
    return None


# <----------

# Helper functions ----------->


def __server_in_sg(sharing_group: GetAllSharingGroupsResponseResponseItem, server: db_Server) -> bool:
    """
    This function checks whether the server is in the sharing group.
    :param sharing_group: The sharing group to check.
    :param server: The server to check.
    :return: Whether the server is in the sharing group.
    """
    if not sharing_group.SharingGroup.roaming:
        cond = False
        for s_g_server in sharing_group.SharingGroupServer:
            if s_g_server.all_orgs:
                return True
            else:
                cond = True
        if not cond and server.internal:
            return False

    for org in sharing_group.SharingGroupOrg:
        if org.org_id == server.remote_org_id:
            return True
    return False
