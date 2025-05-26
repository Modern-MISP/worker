import logging
import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from streaq import WrappedContext

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxies import ExportGalaxyGalaxyElement
from mmisp.api_schemas.galaxy_clusters import (
    GalaxyClusterSearchBody,
    GetGalaxyClusterResponse,
    PutGalaxyClusterRequest,
    SearchGalaxyClusterGalaxyClustersDetails,
)
from mmisp.api_schemas.galaxy_common import GetAllSearchGalaxiesAttributes
from mmisp.api_schemas.organisations import AddOrganisation, GetOrganisationElement
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.shadow_attribute import ShadowAttribute
from mmisp.api_schemas.sharing_groups import (
    GetAllSharingGroupsResponseResponseItem,
    GetAllSharingGroupsResponseResponseItemSharingGroupOrgItem,
    GetAllSharingGroupsResponseResponseItemSharingGroupServerItem,
    ViewUpdateSharingGroupLegacyResponse,
)
from mmisp.api_schemas.sightings import SightingAttributesResponse
from mmisp.db.database import sessionmanager
from mmisp.lib.distribution import DistributionLevels, EventDistributionLevels, GalaxyDistributionLevels
from mmisp.lib.logger import alog
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException, InvalidAPIResponse
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.jobs.sync.sync_config_data import SyncConfigData, sync_config_data
from mmisp.worker.jobs.sync.sync_helper import _get_mini_events_from_server
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import (
    event_id_exists,
    filter_blocked_clusters,
    galaxy_id_exists,
    get_org_by_name,
    get_server,
    sighting_id_exists,
)
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser

from ..queue import queue

JOB_NAME = "pull_job"
__logger = logging.getLogger("mmisp")

# TODO: Remove after debugging or implement env variable
__logger.setLevel("DEBUG")


@queue.task()
async def pull_job(ctx: WrappedContext[None], user_data: UserData, pull_data: PullData) -> PullResult:
    """
    This function represents the pull job. It pulls data from a remote server and saves it in the local server.
    :param user_data: The user data of the user who started the job.
    :param pull_data: The data needed to pull the data from the remote server.
    :return: An object containing the results of the pull job.
    """
    sync_config: SyncConfigData = sync_config_data
    assert sessionmanager is not None
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

            # TODO sightings implementation is wrong, to be fixed
            # pulled_sightings = await __pull_sightings(misp_api, remote_server)

            __logger.info(f"{pulled_sightings} sightings pulled or updated.")
        return PullResult(
            successes=pulled_events,
            fails=failed_pulled_events,
            pulled_proposals=pulled_proposals,
            pulled_sightings=pulled_sightings,
            pulled_clusters=pulled_clusters,
        )


# Functions designed to help with the Galaxy Cluster push ----------->


@alog
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
    user_org: GetOrganisationElement = await misp_api.get_organisation(user.org_id)

    cluster_ids: list[str] = await __get_cluster_id_list_based_on_pull_technique(
        session, misp_api, user, technique, remote_server
    )
    __logger.debug(
        f"Found {len(cluster_ids)} clusters to pull from Server {remote_server.id}.Cluster IDs: {cluster_ids}"
    )

    pulled_clusters: int = 0
    for cluster_id in cluster_ids:
        if await _pull_cluster(session, misp_api, remote_server, cluster_id, user, user_org):
            pulled_clusters += 1

    return pulled_clusters


@alog
async def _pull_cluster(
    session: AsyncSession,
    misp_api: MispAPI,
    remote_server: Server,
    cluster_id: str,
    user: MispUser,
    user_org: GetOrganisationElement,
) -> bool:
    # Load existing cluster
    try:
        existing_cluster: GetGalaxyClusterResponse | None = await misp_api.get_galaxy_cluster(cluster_id)
    except APIException:
        # Cluster does not exist locally
        existing_cluster = None

    if existing_cluster and not existing_cluster.locked and not remote_server.internal:
        __logger.warning(
            f"Cluster {cluster_id} cannot be updated. This can occur if a synchronized cluster, "
            f"originally created on this instance, was modified by an administrator on the remote side."
        )
        return False

    # Fetching remote cluster
    try:
        cluster: GetGalaxyClusterResponse = await misp_api.get_galaxy_cluster(cluster_id, remote_server)
    except APIException as e:
        __logger.warning(
            f"Error while pulling galaxy cluster with id {cluster_id}, "
            f"from Server with id {remote_server.id}: " + str(e)
        )
        return False

    # Skip default cluster
    if cluster.default:
        __logger.info(f"Cluster with id {cluster_id} is a default cluster. Skipping.")
        return False

    # Skip cluster if it has no Galaxy
    if not cluster.Galaxy:
        __logger.error(f"Cluster {cluster.uuid} from Server {remote_server.name} has no galaxy. Cannot be pulled.")
        return False
    else:
        galaxy: GetAllSearchGalaxiesAttributes = cluster.Galaxy

    # Prepare cluster
    cluster = await _update_pulled_cluster_before_insert(session, misp_api, user, user_org, cluster, remote_server)

    if existing_cluster:
        cluster.GalaxyElement = await _update_pulled_cluster_elements_before_insert(
            cluster.GalaxyElement, existing_cluster.id
        )
        cluster.galaxy_id = existing_cluster.galaxy_id
    else:
        cluster.GalaxyElement = await _update_pulled_cluster_elements_before_insert(cluster.GalaxyElement, None)

        # Pull Galaxy
        new_galaxy_id: int = await _pull_cluster_galaxy(session, misp_api, galaxy, user, user_org, remote_server)
        if new_galaxy_id > 0:
            cluster.galaxy_id = new_galaxy_id
        else:
            __logger.error(f"Cluster with id {cluster_id} could not be pulled. Failed to pull galaxy.")
            return False

    return await _save_pulled_cluster(misp_api, existing_cluster, cluster)


@alog
async def _save_pulled_cluster(
    misp_api: MispAPI, local_cluster: GetGalaxyClusterResponse | None, pulled_cluster: GetGalaxyClusterResponse
) -> bool:
    cluster_id: str | None = pulled_cluster.uuid
    if local_cluster:
        try:
            pulled_cluster.id = local_cluster.id
            cluster_updated: bool = await misp_api.update_cluster(
                PutGalaxyClusterRequest(**pulled_cluster.model_dump(exclude_unset=True, mode="json"))
            )
        except APIException as e:
            __logger.error(f"Cluster with id {cluster_id} could not be updated on local server: " + str(e))
            return False

        if cluster_updated:
            __logger.debug(f"Cluster with id {cluster_id} updated successfully on local server.")
            return True
        else:
            __logger.warning(f"Cluster with id {cluster_id} could not be updated on local server.")

    else:
        pulled_cluster.id = None
        try:
            cluster_saved: bool = await misp_api.save_cluster(pulled_cluster)
        except APIException as e:
            __logger.error(f"Cluster with id {cluster_id} could not be saved on local server: " + str(e))
            return False

        if cluster_saved:
            __logger.debug(f"Cluster with id {cluster_id} saved successfully on local server.")
            return True
        else:
            __logger.warning(f"Cluster with id {cluster_id} could not be saved on local server.")
            return False

    return False


@alog
async def _pull_cluster_galaxy(
    session: AsyncSession,
    misp_api: MispAPI,
    galaxy: GetAllSearchGalaxiesAttributes,
    user: MispUser,
    user_org: GetOrganisationElement,
    remote_server: Server,
) -> int:
    if user.role.perm_site_admin and user.role.perm_galaxy_editor:
        galaxy = await _update_pulled_galaxy_before_insert(
            session,
            misp_api,
            galaxy,
            user,
            user_org,
            remote_server,
        )
    else:
        __logger.error(f"Failed to pull Galaxy {galaxy.uuid}. User has no permission to modify galaxies.")
        return -1

    # TODO: Save Galaxy. Endpoint not implemented.
    if await galaxy_id_exists(session, galaxy.uuid):
        return (await misp_api.get_galaxy(galaxy.uuid)).Galaxy.id
    else:
        __logger.error(f"Galaxy with uuid={galaxy.uuid} does not exist locally. Galaxy pull not yet implemented.")
        # return = await misp_api.save_galaxy(cluster.Galaxy)
        return -1


@alog
async def _update_pulled_cluster_before_insert(
    session: AsyncSession,
    misp_api: MispAPI,
    user: MispUser,
    user_org: GetOrganisationElement,
    cluster: GetGalaxyClusterResponse,
    server: Server,
) -> GetGalaxyClusterResponse:
    user_has_perm: bool = user.role.perm_sync or user.role.perm_site_admin or False

    cluster.locked = True
    if not cluster.distribution:
        cluster.distribution = str(GalaxyDistributionLevels.COMMUNITY.value)

    cluster.tag_name = f'misp-galaxy:{cluster.type}="{cluster.uuid}"'

    # TODO: Why ist this permission attribute missing?
    # remote_perm_sync_internal: bool = (await misp_api.get_user(user_id=None, server=server)).role.perm_sync_internal
    remote_perm_sync_internal: bool = False

    if (
        not sync_config_data.misp_host_org_id
        or sync_config_data.misp_host_org_id != server.org_id
        or not server.internal
        or not remote_perm_sync_internal
    ):
        match cluster.distribution:
            case GalaxyDistributionLevels.COMMUNITY:
                cluster.distribution = str(GalaxyDistributionLevels.OWN_ORGANIZATION.value)
            case GalaxyDistributionLevels.CONNECTED_COMMUNITIES:
                cluster.distribution = str(GalaxyDistributionLevels.COMMUNITY.value)

        # TODO: Implement this code in 'updatePulledClusterBeforeInsert()' in GalaxyCluster.php
        # Galaxy Cluster Relation not yet implemented in MMISP
        #     if (!empty($cluster['GalaxyCluster']['GalaxyClusterRelation'])) {
        #       foreach ($cluster['GalaxyCluster']['GalaxyClusterRelation'] as $k = > $relation) {
        #           switch ($relation['distribution']) {
        #               case 1:
        #                   $cluster['GalaxyCluster']['GalaxyClusterRelation'][$k]['distribution'] = 0;
        #                   break;
        #               case 2:
        #                   $cluster['GalaxyCluster']['GalaxyClusterRelation'][$k]['distribution'] = 1;
        #                   break;
        #           }
        #       }
        #     }

    cluster.org_id = server.org_id

    # Only sync users can create cluster on behalf of other users
    if (not cluster.orgc_id and not cluster.Orgc) or (
        (not user_has_perm)
        and (
            (not cluster.Orgc and cluster.orgc_id != user.org_id)
            or (not cluster.orgc_id and (not cluster.Orgc or cluster.Orgc.uuid != user_org.uuid))
        )
    ):
        cluster.orgc_id = cluster.org_id

    # Capture Sharing Group
    await _capture_sharing_group_for_cluster(misp_api, cluster, user, server)

    # Capture Orgc

    if cluster.Orgc:
        new_orgc_id: int | None = await _capture_orgc(session, misp_api, cluster.Orgc)
        if new_orgc_id:
            cluster.orgc_id = new_orgc_id
        else:
            __logger.warning(f"Error while capturing orgc id for cluster {cluster.uuid}. Assigned org_id of user.")
            cluster.orgc_id = user.org_id
    else:
        cluster.orgc_id = user.org_id

    return cluster


@alog
async def _update_pulled_galaxy_before_insert(
    session: AsyncSession,
    misp_api: MispAPI,
    galaxy: GetAllSearchGalaxiesAttributes,
    user: MispUser,
    user_org: GetOrganisationElement,
    server: Server,
) -> GetAllSearchGalaxiesAttributes:
    user_has_perm: bool = user.role.perm_sync or user.role.perm_site_admin

    galaxy_orgc: GetOrganisationElement = await misp_api.get_organisation(galaxy.orgc_id, server)
    galaxy.org_id = server.org_id

    if (not galaxy.orgc_id and not galaxy_orgc) or (
        (not user_has_perm)
        and ((not galaxy_orgc and galaxy.orgc_id != user.org_id) or (galaxy_orgc.uuid != user_org.uuid))
    ):
        galaxy.orgc_id = galaxy.org_id

    galaxy.default = False

    # Capture Sharing Group
    if galaxy.distribution and galaxy.distribution == 4:
        galaxy.distribution == DistributionLevels.OWN_ORGANIZATION

    # Capture Orgc

    new_orgc_id: int | None = await _capture_orgc(session, misp_api, galaxy_orgc)
    if new_orgc_id:
        galaxy.orgc_id = new_orgc_id
    else:
        __logger.warning(f"Error while capturing orgc id for galaxy {galaxy.uuid}. Assigned org_id of user.")
    galaxy.orgc_id = user.org_id

    return galaxy


@alog
async def _update_pulled_cluster_elements_before_insert(
    cluster_elements: list[ExportGalaxyGalaxyElement], cluster_id: int | None
) -> list[ExportGalaxyGalaxyElement]:
    updated_elements: list[ExportGalaxyGalaxyElement] = []

    for cluster_element in cluster_elements:
        cluster_element.id = None
        cluster_element.galaxy_cluster_id = cluster_id

        updated_elements.append(cluster_element)

    return updated_elements


async def _capture_sharing_group_for_cluster(
    misp_api: MispAPI,
    cluster: GetGalaxyClusterResponse,
    user: MispUser,
    server: Server,
) -> None:
    if cluster.distribution and cluster.distribution != GalaxyDistributionLevels.SHARING_GROUP:
        cluster.sharing_group_id = None
        return

    if cluster.sharing_group_id:
        remote_sharing_group: ViewUpdateSharingGroupLegacyResponse = await misp_api.get_sharing_group(
            cluster.sharing_group_id, server
        )
        local_sharing_group: ViewUpdateSharingGroupLegacyResponse | None = await misp_api.get_sharing_group(
            remote_sharing_group.SharingGroup.uuid
        )

        if local_sharing_group and (
            user.role.perm_site_admin
            or user.org_id == local_sharing_group.Organisation.id
            or any(
                sharing_group_server.server_id == 0 and sharing_group_server.all_orgs
                for sharing_group_server in local_sharing_group.SharingGroupServer
            )
            or any(sharing_group_org.org_id == user.org_id for sharing_group_org in local_sharing_group.SharingGroupOrg)
        ):
            cluster.sharing_group_id = str(local_sharing_group.SharingGroup.id)
            return

    cluster.sharing_group_id = "0"
    cluster.distribution = str(GalaxyDistributionLevels.OWN_ORGANIZATION.value)


@alog
async def _capture_orgc(session: AsyncSession, misp_api: MispAPI, orgc: GetOrganisationElement) -> int | None:
    """
    :return: The id of the captured organisation, None otherwise.
    """
    local_org: GetOrganisationElement | None = None
    try:
        if orgc.uuid:
            local_org = await misp_api.get_organisation(orgc.uuid)
        else:
            local_org = await get_org_by_name(session, orgc.name)
    except APIException:
        # --> Organisation does not exist locally.
        __logger.debug(f"Creator Org '{orgc.name}' of pulled cluster does not exist locally.")

    # If orgc exists locally
    if local_org:
        return local_org.id
    else:
        new_org_body: AddOrganisation = AddOrganisation(**orgc.model_dump(mode="json"))
        new_org_body.id = None
        new_org_body.local = False

        if orgc.uuid:
            new_org_body.name = f"{orgc.name}_{uuid.uuid4()}"

        try:
            new_org: GetOrganisationElement = await misp_api.save_organisation(new_org_body)
        except APIException as e:
            __logger.error(f"Error while creating organisation '{orgc.name}' with uuid={orgc.uuid} locally: " + str(e))
            return None
        return new_org.id


@alog
async def __get_cluster_id_list_based_on_pull_technique(
    session: AsyncSession, misp_api: MispAPI, user: MispUser, technique: PullTechniqueEnum, remote_server: Server
) -> list[str]:
    """
    This function returns a list of galaxy cluster uuids based on the pull technique.
    :param user: The user who started the job.
    :param technique: The technique used to pull the galaxy clusters.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster uuids.
    """
    if technique == PullTechniqueEnum.INCREMENTAL or technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return await __get_local_cluster_uuids_from_server_for_pull(session, misp_api, user, remote_server)
    else:
        return await __get_all_cluster_uuids_from_server_for_pull(session, misp_api, user, remote_server)


@alog
async def __get_local_cluster_uuids_from_server_for_pull(
    session: AsyncSession, misp_api: MispAPI, user: MispUser, remote_server: Server
) -> list[str]:
    """
    This function returns a list of galaxy cluster uuids, from the locale server, based on the pull technique.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster uuids.
    """

    local_galaxy_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await __get_accessible_local_cluster(
        misp_api, user
    )
    if len(local_galaxy_clusters) == 0:
        return []
    conditions: GalaxyClusterSearchBody = GalaxyClusterSearchBody(published=True, minimal=True, custom=True)
    remote_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(
        conditions, remote_server
    )
    local_uuid_dic: dict[str, SearchGalaxyClusterGalaxyClustersDetails] = {
        cluster.uuid: cluster for cluster in local_galaxy_clusters
    }
    remote_clusters = __get_intersection(local_uuid_dic, remote_clusters)
    remote_clusters = await filter_blocked_clusters(session, remote_clusters)
    out: list[str] = []
    for cluster in remote_clusters:
        if int(local_uuid_dic[cluster.uuid].version) < int(cluster.version):
            out.append(cluster.uuid)
    return out


@alog
async def __get_all_cluster_uuids_from_server_for_pull(
    session: AsyncSession, misp_api: MispAPI, user: MispUser, remote_server: Server
) -> list[str]:
    """
    This function returns a list of galaxy cluster uuids, from the remote server, based on the pull technique.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster uuids.
    """

    conditions: GalaxyClusterSearchBody = GalaxyClusterSearchBody(published=True, minimal=True, custom=True)
    remote_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(
        conditions, remote_server
    )
    remote_clusters = await filter_blocked_clusters(session, remote_clusters)

    local_galaxy_clusters: list[GetGalaxyClusterResponse] = await __get_all_clusters_with_id(
        misp_api, [cluster.uuid for cluster in remote_clusters]
    )
    local_id_dic: dict[str, GetGalaxyClusterResponse] = {
        cluster.uuid: cluster for cluster in local_galaxy_clusters if cluster.uuid
    }
    out: list[str] = []
    for cluster in remote_clusters:
        if cluster.uuid not in local_id_dic or local_id_dic[cluster.uuid].version < int(cluster.version):
            out.append(cluster.uuid)
    return out


@alog
async def __get_accessible_local_cluster(
    misp_api: MispAPI, user: MispUser
) -> list[SearchGalaxyClusterGalaxyClustersDetails]:
    """
    This function returns a list of galaxy clusters that the user has access to.
    :param user: The user who started the job.
    :return: A list of galaxy clusters.
    """

    conditions: GalaxyClusterSearchBody = GalaxyClusterSearchBody(published=True, minimal=True, custom=True)
    local_galaxy_clusters: list[SearchGalaxyClusterGalaxyClustersDetails] = await misp_api.get_custom_clusters(
        conditions
    )

    if not user.role.perm_site_admin:
        sharing_ids: list[int] = await __get_sharing_group_ids_of_user(misp_api, user)
        out: list[SearchGalaxyClusterGalaxyClustersDetails] = []
        for cluster in local_galaxy_clusters:
            if (
                cluster.org_id == user.org_id
                and cluster.distribution
                and 0 < int(cluster.distribution) < 4
                and cluster.sharing_group_id in sharing_ids
            ):
                out.append(cluster)
        return out

    return local_galaxy_clusters


@alog
async def __get_all_clusters_with_id(misp_api: MispAPI, ids: list[int | str]) -> list[GetGalaxyClusterResponse]:
    """
    This function returns a list of galaxy clusters with the given ids or uuids.
    :param ids: The ids or uuids of the galaxy clusters.
    :return: A list of galaxy clusters.
    """
    out: list[GetGalaxyClusterResponse] = []
    for cluster_id in ids:
        try:
            out.append(await misp_api.get_galaxy_cluster(cluster_id))
        except APIException:
            # Cluster does not exist locally
            pass

    return out


@alog
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


@alog
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
    __logger.debug(
        f"Found {len(remote_event_ids)} events to pull from Server {remote_server.name}. Event IDs: {remote_event_ids}"
    )

    for event_id in remote_event_ids:
        if await __pull_event(session, misp_api, event_id, remote_server):
            pulled_events += 1
        else:
            __logger.info(f"Event with id {event_id} already exists and is up to date.")
    failed_pulled_events: int = len(remote_event_ids) - pulled_events
    return pulled_events, failed_pulled_events


@alog
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


@alog
async def __pull_event(session: AsyncSession, misp_api: MispAPI, event_id: int, remote_server: Server) -> bool:
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

    remote_orgc: GetOrganisationElement = await misp_api.get_organisation(event.orgc_id, remote_server)
    local_orgc: GetOrganisationElement | None
    try:
        local_orgc = await misp_api.get_organisation(remote_orgc.uuid) if remote_orgc.uuid else None
    except APIException:
        local_orgc = None

    if not local_orgc:
        __logger.warning(
            f"Event {event.uuid}, cannot be pulled. Organisation with id {event.orgc_id} not found locally."
        )
        return False

    updated_event: AddEditGetEventDetails = await _update_pulled_event_before_insert(event, local_orgc, remote_server)

    if await event_id_exists(session, updated_event.uuid):
        if await misp_api.update_event(updated_event):
            __logger.debug(f"Event {updated_event.uuid} updated. Update pulled from Server {remote_server.id}.")
            return True
        else:
            __logger.warning(
                f"Error while pulling Event with id {updated_event.uuid} from Server with id {remote_server.id}. "
                f"Event should exist locally but cannot be updated."
            )
            return False
    else:
        if await misp_api.save_event(updated_event):
            __logger.debug(f"Event {updated_event} saved locally. Pulled from Server {remote_server.id}.")
            return True
        else:
            __logger.warning(
                f"Error while pulling Event with id {updated_event.uuid} from Server with id {remote_server.id}. "
                f"Event should not exist locally but cannot be saved."
            )

    return False


@alog
async def _update_pulled_event_before_insert(
    event: AddEditGetEventDetails, orgc: GetOrganisationElement, remote_server: Server
) -> AddEditGetEventDetails:
    """
    This function prepares the fetched event for pull.
    :param event: The event to be prepared.
    :return: The prepared event.
    """

    event.org_id = remote_server.org_id
    event.orgc_id = orgc.id

    # The event came from pull, so it should be locked
    event.locked = True

    if (
        not sync_config_data.misp_host_org_id
        or sync_config_data.misp_host_org_id
        or not remote_server.internal
        or sync_config_data.misp_host_org_id != remote_server.org_id
    ):
        match event.distribution:
            case EventDistributionLevels.COMMUNITY:
                event.distribution = EventDistributionLevels.OWN_ORGANIZATION
            case EventDistributionLevels.CONNECTED_COMMUNITIES:
                event.distribution = EventDistributionLevels.COMMUNITY

    return event


@alog
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
@alog
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
                f"Error while pulling proposal for Event with id {proposal.event_id}, "
                f"from Server with id {remote_server.id}: " + str(e)
            )
    return pulled_proposals


# <-----------
# Functions designed to help with the Sighting pull ----------->


# TODO: Sightings implementation is wrong, to be fixed
@alog
async def __pull_sightings(session: AsyncSession, misp_api: MispAPI, remote_server: Server) -> int:
    """
    This function pulls the sightings from the remote server and saves them in the local server.
    :param remote_server: The remote server from which the sightings are pulled.
    :return: The number of pulled sightings.
    """

    remote_event_views: list[MispMinimalEvent] = await misp_api.get_minimal_events(False, remote_server)

    local_event_views: list[MispMinimalEvent] = await misp_api.get_minimal_events(True)
    local_event_ids_dic: dict[str, MispMinimalEvent] = {event.uuid: event for event in local_event_views if event.uuid}

    remote_event_ids: list[int] = []
    for remote_event in remote_event_views:
        if remote_event.uuid in local_event_ids_dic and (
            remote_event.timestamp > local_event_ids_dic[remote_event.uuid].timestamp
        ):
            remote_event_ids.append(remote_event.id)

    fetched_sightings: list[SightingAttributesResponse] = []
    for event_id in remote_event_ids:
        try:
            fetched_sightings.extend(await misp_api.get_sightings_from_event(event_id, remote_server))
        except Exception as e:
            __logger.warning(
                f"Error while pulling Sightings from Event with id {event_id}, "
                f"from Server with id {remote_server.id}: " + str(e)
            )

    pulled_sightings: int = 0
    for sighting in fetched_sightings:
        if sighting_id_exists(session, sighting.uuid):
            __logger.debug(f"Sighting with uuid {sighting.uuid} already exists locally. Skipping.")
        else:
            if await misp_api.save_sighting(sighting):
                pulled_sightings += 1
            else:
                __logger.error(f"Sighting with uuid {sighting.uuid} could not be pulled.")

    return pulled_sightings


def __get_intersection(
    cluster_dic: dict[str, SearchGalaxyClusterGalaxyClustersDetails],
    cluster_list: list[SearchGalaxyClusterGalaxyClustersDetails],
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
            if cluster.uuid == local_cluster_id:
                out.append(cluster)
    return out
