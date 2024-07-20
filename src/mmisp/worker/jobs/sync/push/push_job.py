import json
import logging
import re

from mmisp.api_schemas.events import AddEditGetEventDetails, AddEditGetEventTag
from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.api_schemas.server import Server, ServerVersion
from mmisp.api_schemas.sharing_groups import GetAllSharingGroupsResponseResponseItem
from mmisp.api_schemas.sightings import SightingAttributesResponse
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client.celery_client import celery_app
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings
from mmisp.worker.jobs.sync.push.job_data import PushData, PushResult, PushTechniqueEnum
from mmisp.worker.jobs.sync.push.push_worker import push_worker
from mmisp.worker.jobs.sync.sync_helper import _get_mini_events_from_server
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent

__logger = logging.getLogger(__name__)


@celery_app.task
async def push_job(user_data: UserData, push_data: PushData) -> PushResult:
    """
    This function represents the push job. It pushes the data to the remote server.
    :param user_data: The user data of the user that started the job.
    :param push_data: The push data that contains the server id and the technique.
    :return: The result of the push job.
    """
    server_id: int = push_data.server_id
    technique: PushTechniqueEnum = push_data.technique

    remote_server: Server = await push_worker.misp_api.get_server(server_id)
    server_version: ServerVersion = await push_worker.misp_api.get_server_version(remote_server)

    if not remote_server.push or not server_version.perm_sync and not server_version.perm_sighting:
        raise ForbiddenByServerSettings("Remote instance is outdated or no permission to push.")

    # check whether server allows push
    sharing_groups: list[GetAllSharingGroupsResponseResponseItem] = await push_worker.misp_api.get_sharing_groups()
    if remote_server.push and server_version.perm_sync:
        if remote_server.push_galaxy_clusters:
            pushed_clusters: int = await __push_clusters(remote_server)
            __logger.info(f"Pushed {pushed_clusters} clusters to server {remote_server.id}")

        pushed_events: int = await __push_events(technique, sharing_groups, server_version, remote_server)
        __logger.info(f"Pushed {pushed_events} events to server {remote_server.id}")
        pushed_proposals: int = await __push_proposals(remote_server)
        __logger.info(f"Pushed {pushed_proposals} proposals to server {remote_server.id}")

    if remote_server.push_sightings and server_version.perm_sighting:
        pushed_sightings: int = await __push_sightings(sharing_groups, remote_server)
        __logger.info(f"Pushed {pushed_sightings} sightings to server {remote_server.id}")
    return PushResult(success=True)


# Functions designed to help with the Galaxy Cluster push ----------->


async def __push_clusters(remote_server: Server) -> int:
    """
    This function pushes the clusters in the local server to the remote server.
    :param remote_server: The remote server to push the clusters to.
    :return: The number of clusters that were pushed.
    """

    conditions: dict = {"published": True, "minimal": True, "custom": True}
    clusters: list[GetGalaxyClusterResponse] = await push_worker.misp_api.get_custom_clusters(conditions)
    clusters = await __remove_older_clusters(clusters, remote_server)
    cluster_success: int = 0
    for cluster in clusters:
        if push_worker.misp_api.save_cluster(cluster, remote_server):
            cluster_success += 1
        else:
            __logger.info(f"Cluster with id {cluster.id} already exists on server {remote_server.id}.")
    return cluster_success


async def __remove_older_clusters(
    clusters: list[GetGalaxyClusterResponse], remote_server: Server
) -> list[GetGalaxyClusterResponse]:
    """
    This function removes the clusters that are older than the ones on the remote server.
    :param clusters: The clusters to check.
    :param remote_server: The remote server to check the clusters against.
    :return: The clusters that are not older than the ones on the remote server.
    """
    conditions: dict = {"published": True, "minimal": True, "custom": True, "id": clusters}
    remote_clusters: list[GetGalaxyClusterResponse] = await push_worker.misp_api.get_custom_clusters(
        conditions, remote_server
    )
    remote_clusters_dict: dict[int, GetGalaxyClusterResponse] = {cluster.id: cluster for cluster in remote_clusters}
    out: list[GetGalaxyClusterResponse] = []
    for cluster in clusters:
        if cluster.id in remote_clusters_dict and remote_clusters_dict[cluster.id].version <= cluster.version:
            out.append(cluster)
    return remote_clusters


# <----------

# Functions designed to help with the Event push ----------->


async def __push_events(
    technique: PushTechniqueEnum,
    sharing_groups: list[GetAllSharingGroupsResponseResponseItem],
    server_version: ServerVersion,
    remote_server: Server,
) -> int:
    """
    This function pushes the events in the local server based on the technique to the remote server.
    :param technique: The technique to use.
    :param sharing_groups: The sharing groups of the local server.
    :param server_version: The version of the remote server.
    :param remote_server: The remote server to push the events to.
    :return: The number of events that were pushed.
    """
    server_sharing_group_ids: list[int] = []
    for sharing_group in sharing_groups:
        if not __server_in_sg(sharing_group, remote_server):
            server_sharing_group_ids.append(int(sharing_group.SharingGroup.id))

    local_events: list[AddEditGetEventDetails] = await __get_local_event_views(
        server_sharing_group_ids, technique, remote_server
    )
    event_ids = [
        event.id for event in local_events
    ]  # push_worker.misp_api.filter_events_for_push(local_events, remote_server)
    pushed_events: int = 0
    for event_id in event_ids:
        if __push_event(event_id, server_version, technique, remote_server):
            pushed_events += 1
        else:
            __logger.info(f"Event with id {event_id} already exists on server {remote_server.id} and is up to date.")
    return pushed_events


async def __get_local_event_views(
    server_sharing_group_ids: list[int], technique: PushTechniqueEnum, server: Server
) -> list[AddEditGetEventDetails]:
    mini_events: list[MispMinimalEvent] = await push_worker.misp_api.get_minimal_events(True)  # server -> None

    if technique == PushTechniqueEnum.INCREMENTAL:
        for mini_event in mini_events:
            if (server.lastpushedid is None) or mini_event.id <= server.lastpushedid:
                mini_events.remove(mini_event)

    events: list[AddEditGetEventDetails] = []
    for event_view in mini_events:
        try:
            event: AddEditGetEventDetails = await push_worker.misp_api.get_event(event_view.id)
            events.append(event)
        except Exception as e:
            __logger.warning(f"Could not get event {event_view.id} from server {server.id}: {e}")

    out: list[AddEditGetEventDetails] = []
    for event in events:
        if (
            event.published
            and len(event.Attribute) > 0
            and 0 < event.distribution < 4
            or event.distribution == 4
            and event.sharing_group_id in server_sharing_group_ids
        ):
            out.append(event)

    return out


async def __push_event(
    event_id: int, server_version: ServerVersion, technique: PushTechniqueEnum, server: Server
) -> bool:
    """
    This function pushes the event with the given id to the remote server. It also pushes the clusters if the server
    and technique allows it.
    :param event_id: The id of the event to push.
    :param server_version: The version of the remote server.
    :param technique: The technique to use.
    :param server: The remote server.
    :return: Whether the event was pushed.
    """

    try:
        event: AddEditGetEventDetails = await push_worker.misp_api.get_event(event_id)
    except Exception as e:
        __logger.warning(f"Could not get event {event_id} from server {server.id}: {e}")
        return False
    if server_version.perm_galaxy_editor and server.push_galaxy_clusters and technique == PushTechniqueEnum.FULL:
        await __push_event_cluster_to_server(event, server)

    if not await push_worker.misp_api.save_event(event, server):
        return await push_worker.misp_api.update_event(event, server)
    return True


async def __push_event_cluster_to_server(event: AddEditGetEventDetails, server: Server) -> int:
    """
    This function pushes the clusters of the event to the remote server.
    :param event: The event to push the clusters of.
    :param server: The remote server.
    :return: The number of clusters that were pushed.
    """
    tags: list[AddEditGetEventTag] = event.Tag
    tag_names: list[str] = [tag.name for tag in tags]
    custom_cluster_tagnames: list[str] = list(filter(__is_custom_cluster_tag, tag_names))

    conditions: dict = {"published": True, "minimal": True, "custom": True}
    all_clusters: list[GetGalaxyClusterResponse] = await push_worker.misp_api.get_custom_clusters(conditions)
    clusters: list[GetGalaxyClusterResponse] = []
    for cluster in all_clusters:
        if cluster.tag_name in custom_cluster_tagnames:
            clusters.append(cluster)

    clusters = await __remove_older_clusters(clusters, server)
    cluster_succes: int = 0
    for cluster in clusters:
        if push_worker.misp_api.save_cluster(cluster, server):
            cluster_succes += 1
        else:
            __logger.warning(f"Could not push event cluster {cluster.id} to server {server.id}")
    return cluster_succes


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
async def __push_proposals(remote_server: Server) -> int:
    """
    This function pushes the proposals in the local server to the remote server.
    :param remote_server: The remote server to push the proposals to.
    :return: The number of proposals that were pushed.
    """
    local_event_views: list[MispMinimalEvent] = await push_worker.misp_api.get_minimal_events(True)
    local_event_ids: list[int] = [event.id for event in local_event_views]
    misp_api = push_worker.misp_api
    event_views: list[MispMinimalEvent] = await _get_mini_events_from_server(
        True, local_event_ids, push_worker.sync_config, misp_api, remote_server
    )
    out: int = 0
    for event_view in event_views:
        try:
            event: AddEditGetEventDetails = await push_worker.misp_api.get_event(event_view.id)
            if push_worker.misp_api.save_proposal(event, remote_server):
                out += 1
            else:
                __logger.info(f"Proposal for event with id {event.id} already exists on server {remote_server.id}.")
        except Exception as e:
            __logger.warning(f"Could not get event {event_view.id} from server {remote_server.id}: {e}")
    return out


# <----------

# Functions designed to help with the Sighting push ----------->


async def __push_sightings(sharing_groups: list[GetAllSharingGroupsResponseResponseItem], remote_server: Server) -> int:
    """
    This function pushes the sightings in the local server to the remote server.
    :param sharing_groups: The sharing groups of the local server.
    :param remote_server: The remote server to push the sightings to.
    :return: The number of sightings that were pushed.
    """
    misp_api = push_worker.misp_api
    remote_event_views: list[MispMinimalEvent] = await _get_mini_events_from_server(
        True, [], push_worker.sync_config, misp_api, remote_server
    )
    local_event_views: list[MispMinimalEvent] = await push_worker.misp_api.get_minimal_events(True)
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
            event: AddEditGetEventDetails = await push_worker.misp_api.get_event(event_id)
        except Exception as e:
            __logger.warning(f"Could not get event {event_id} from server {remote_server.id}: {e}")
            continue
        if not __allowed_by_push_rules(event, remote_server):
            continue
        if not __allowed_by_distribution(event, sharing_groups, remote_server):
            continue

        remote_sightings: set[SightingAttributesResponse] = set(
            await push_worker.misp_api.get_sightings_from_event(event.id, remote_server)
        )
        local_sightings: set[SightingAttributesResponse] = set(
            await push_worker.misp_api.get_sightings_from_event(event.id)
        )
        new_sightings: list[SightingAttributesResponse] = list()
        for local_sighting in local_sightings:
            if local_sighting.id not in remote_sightings:
                new_sightings.append(local_sighting)

        if len(new_sightings) == 0:
            continue

        for sighting in new_sightings:
            if push_worker.misp_api.save_sighting(sighting, remote_server):
                success += 1
            else:
                __logger.info(f"Sighting with id {sighting.id} already exists on server {remote_server.id}.")
    return success


def __allowed_by_push_rules(event: AddEditGetEventDetails, server: Server) -> bool:
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
    event: AddEditGetEventDetails, sharing_groups: list[GetAllSharingGroupsResponseResponseItem], server: Server
) -> bool:
    """
    This function checks whether the push of the event-sightings is allowed by the distribution of the event.
    :param event: The event to check.
    :param sharing_groups: The sharing groups of the local server.
    :param server: The remote server.
    :return: Whether the event-sightings are allowed by the distribution of the event.
    """
    if not server.internal or push_worker.sync_config.misp_host_org_id != server.remote_org_id:
        if event.distribution < 2:
            return False
    if event.distribution == 4:
        sharing_group: GetAllSharingGroupsResponseResponseItem | None = __get_sharing_group(
            event.sharing_group_id, sharing_groups
        )
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


def __server_in_sg(sharing_group: GetAllSharingGroupsResponseResponseItem, server: Server) -> bool:
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
