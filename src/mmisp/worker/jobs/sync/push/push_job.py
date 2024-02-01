from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings, ServerNotReachable
from mmisp.worker.jobs.sync.push.job_data import PushData, PushResult, PushTechniqueEnum
from mmisp.worker.jobs.sync.sync_helper import _get_event_views_from_server, _get_local_events_dic
from mmisp.worker.misp_database.misp_api import JsonType
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.jobs.sync.push.push_worker import push_worker
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
import re

from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship


@celery_app.task
def push_job(user_data: UserData, push_data: PushData) -> PushResult:
    """
    This function represents the push job. It pushes the data to the remote server.
    :param user_data: The user data of the user that started the job.
    :param push_data: The push data that contains the server id and the technique.
    :return: The result of the push job.
    """
    server_id: int = push_data.server_id
    technique: PushTechniqueEnum = push_data.technique

    remote_server: MispServer = push_worker.misp_api.get_server(server_id)


    server_version: MispServerVersion = push_worker.misp_api.get_server_version(remote_server)

    if (not remote_server.push or not server_version.perm_sync
            and not server_version.perm_sighting):
        raise ForbiddenByServerSettings('Remote instance is outdated or no permission to push.')

    pushed_clusters: int = 0
    pushed_events: int = 0
    pushed_proposals: int = 0
    # check whether server allows push
    sharing_groups: list[MispSharingGroup] = push_worker.misp_api.get_sharing_groups()
    if remote_server.push and server_version.perm_sync:
        if remote_server.push_galaxy_clusters:
            pushed_clusters = __push_clusters(remote_server)
        pushed_events = __push_events(technique, sharing_groups, server_version, remote_server)
        pushed_proposals = __push_proposals(remote_server)

    if remote_server.push_sightings and server_version.perm_sighting:
        __push_sightings(sharing_groups, remote_server)
        pass
    return PushResult(succes=True)


# Functions designed to help with the Galaxy Cluster push ----------->

def __push_clusters(remote_server: MispServer) -> int:
    """
    This function pushes the clusters in the local server to the remote server.
    :param remote_server: The remote server to push the clusters to.
    :return: The number of clusters that were pushed.
    """
    clusters: list[MispGalaxyCluster] = push_worker.misp_sql.get_galaxy_clusters("")
    clusters = __remove_older_clusters(clusters, remote_server)
    cluster_succes: int = 0
    for cluster in clusters:
        succes: bool = push_worker.misp_api.save_cluster(cluster, remote_server)
        if succes:
            cluster_succes += 1
    return cluster_succes


def __remove_older_clusters(clusters: list[MispGalaxyCluster], remote_server: MispServer) -> list[MispGalaxyCluster]:
    """
    This function removes the clusters that are older than the ones on the remote server.
    :param clusters: The clusters to check.
    :param remote_server: The remote server to check the clusters against.
    :return: The clusters that are not older than the ones on the remote server.
    """
    conditions: JsonType = {"published": True, "minimal": True, "custom": True, "id": clusters}
    remote_clusters: list[MispGalaxyCluster] = (
        push_worker.misp_api.get_custom_cluster_from_server(conditions, remote_server))
    remote_clusters_dict: dict[int, MispGalaxyCluster] = {cluster.id: cluster for cluster in remote_clusters}
    out: list[MispGalaxyCluster] = []
    for cluster in clusters:
        if cluster.id in remote_clusters_dict and remote_clusters_dict[cluster.id].version <= cluster.version:
            out.append(cluster)
    return remote_clusters


# <----------

# Functions designed to help with the Event push ----------->

def __push_events(technique: PushTechniqueEnum, sharing_groups: list[MispSharingGroup],
                  server_version: MispServerVersion, remote_server: MispServer) -> int:
    """
    This function pushes the events in the local server based on the technique to the remote server.
    :param technique: The technique to use.
    :param sharing_groups: The sharing groups of the local server.
    :param server_version: The version of the remote server.
    :param remote_server: The remote server to push the events to.
    :return: The number of events that were pushed.
    """
    server_sharing_group_ids: list[int] = []
    server: MispServer = push_worker.misp_api.get_server(remote_server.id)
    for sharing_group in sharing_groups:
        if not __server_in_sg(sharing_group, server):
            server_sharing_group_ids.append(sharing_group.id)

    event_sql_query = __generate_event_sql_query(server_sharing_group_ids, technique, remote_server)
    event_ids: list[int] = push_worker.misp_sql.get_event_ids(event_sql_query)
    event_ids = push_worker.misp_api.filter_event_ids_for_push(event_ids, remote_server)
    pushed_events: int = 0
    for event_id in event_ids:
        if __push_event(event_id, server_version, technique, remote_server):
            pushed_events += 1
    return pushed_events


def __generate_event_sql_query(server_sharing_group_ids: list[int], technique: PushTechniqueEnum,
                               server: MispServer) -> str:
    """
    This function generates the sql query to get the events to push based on the technique.
    :param server_sharing_group_ids: The intersection of the sharing groups of the local and remote server.
    :param technique: The technique to use.
    :param server: The remote server.
    :return: The sql query to get the events to push.
    """
    technique_query: str = ""
    if technique == PushTechniqueEnum.INCREMENTAL:
        technique_query = f"id > {server.last_pushed_id} AND"
    table_name: str = "?????IDK?????"
    event_reported_query: str = (f"'EXISTS (SELECT id, deleted FROM {table_name} WHERE {table_name}.event_id = "
                                 f"Event.id and {table_name}.deleted = 0)")
    query: str = technique_query + (f" AND published = 1 AND (attribute_count > 0 OR {event_reported_query}) AND "
                                    f"(distribution > 0 AND distribution < 4 OR distribution = 4 AND sharing_group_id "
                                    f"IN"
                                    f"{tuple(server_sharing_group_ids)})")
    return query


def __push_event(event_id: int, server_version: MispServerVersion, technique: PushTechniqueEnum,
                 server: MispServer) -> bool:
    """
    This function pushes the event with the given id to the remote server. It also pushes the clusters if the server
    and technique allows it.
    :param event_id: The id of the event to push.
    :param server_version: The version of the remote server.
    :param technique: The technique to use.
    :param server: The remote server.
    :return: Whether the event was pushed.
    """
    event: MispEvent = push_worker.misp_api.get_event_from_server(event_id, None)
    if server_version.perm_galaxy_editor and server.push_galaxy_clusters and technique == PushTechniqueEnum.FULL:
        __push_event_cluster_to_server(event, server)
    return push_worker.misp_api.save_event(event, server)


# def __get_event_ids_to_push(user_id: int, server_id: int) -> list[int]:
#     # using sharing_group id for fetch_event_ids
#     sharing_group_ids = push_worker.misp_api.get_sharing_groups_ids(-1)
#     event_ids: list[int] = push_worker.misp_sql.get_event_ids("")
#     return push_worker.misp_sql.filter_event_ids_for_push(event_ids, server_id)


# def __fetch_event(user_id: int, event_id: int) -> MispEvent:
#     return push_worker.misp_api.get_event_from_server(event_id, None)


def __push_event_cluster_to_server(event: MispEvent, server: MispServer) -> int:
    """
    This function pushes the clusters of the event to the remote server.
    :param event: The event to push the clusters of.
    :param server: The remote server.
    :return: The number of clusters that were pushed.
    """
    tags: list[tuple[MispTag, EventTagRelationship]] = event.tags
    tag_names: list[str] = [tag[0].name for tag in tags]
    custom_cluster_tags: list[str] = list(filter(__is_custom_cluster_tag, tag_names))
    query: str = f"tag_name IN {tuple(custom_cluster_tags)}"
    clusters: list[MispGalaxyCluster] = push_worker.misp_sql.get_galaxy_clusters(query)
    clusters = __remove_older_clusters(clusters, server)
    cluster_succes: int = 0
    for cluster in clusters:
        succes: bool = push_worker.misp_api.save_cluster(cluster, server)
        if succes:
            cluster_succes += 1
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
def __push_proposals(remote_server: MispServer) -> int:
    """
    This function pushes the proposals in the local server to the remote server.
    :param remote_server: The remote server to push the proposals to.
    :return: The number of proposals that were pushed.
    """
    local_event_ids = push_worker.misp_sql.get_event_ids("")
    events: list[MispEvent] = _get_event_views_from_server(True, local_event_ids, remote_server)
    out: int = 0
    for event_view in events:
        event: MispEvent = push_worker.misp_api.get_event(event_view.id)
        if push_worker.misp_api.save_proposal(event, remote_server):
            out += 1
    return out


# <----------

# Functions designed to help with the Sighting push ----------->

def __push_sightings(sharing_groups: list[MispSharingGroup], remote_server: MispServer) -> int:
    """
    This function pushes the sightings in the local server to the remote server.
    :param sharing_groups: The sharing groups of the local server.
    :param remote_server: The remote server to push the sightings to.
    :return: The number of sightings that were pushed.
    """
    remote_event_views: list[MispEvent] = _get_event_views_from_server(True, [], remote_server)
    local_event_ids: list[int] = push_worker.misp_sql.get_event_ids("")
    local_event_ids_dic: dict[int, MispEvent] = _get_local_events_dic(local_event_ids)

    target_event_ids: list[int] = []
    for remote_event_view in remote_event_views:
        id: int = remote_event_view.id
        if id in local_event_ids_dic and local_event_ids_dic[id].timestamp > remote_event_view.timestamp:
            target_event_ids.append(id)

    succes: int = 0
    for event_id in target_event_ids:
        event: MispEvent = push_worker.misp_api.get_event_from_server(event_id, None)
        if not __allowed_by_push_rules(event, remote_server):
            continue
        if not __allowed_by_distribution(event, sharing_groups, remote_server):
            continue

        remote_sightings: set[MispSighting] = set(push_worker.misp_api.get_sightings_from_event(event.id,
                                                                                                remote_server))
        local_sightings: set[MispSighting] = set(push_worker.misp_api.get_sightings_from_event(event.id,
                                                                                               None))
        new_sightings: list[MispSighting] = list()
        for local_sighting in local_sightings:
            if local_sighting.id not in remote_sightings:
                new_sightings.append(local_sighting)

        if len(new_sightings) == 0:
            continue

        for sighting in new_sightings:
            if push_worker.misp_api.save_sighting(sighting, remote_server):
                succes += 1
    return succes


def __allowed_by_push_rules(event: MispEvent, server: MispServer) -> bool:
    """
    This function checks whether the push of the event-sightings is allowed by the push rules of the remote server.
    :param event: The event to check.
    :param server: The remote server.
    :return: Whether the event-sightings are allowed by the push rules of the remote server.
    """
    push_rules: dict[str, dict[str, set[str]]] = server.push_rules
    tags: set[str] = {str(tag[0]) for tag in event.tags}
    if "tag" in push_rules and "OR" in push_rules["tag"]:
        if len(push_rules["tag"]["OR"] & tags) == 0:
            return False

    if "tag" in push_rules and "NOT" in push_rules["tag"]:
        if len(push_rules["tag"]["NOT"] & tags) != 0:
            return False

    if "orgs" in push_rules and "OR" in push_rules["tag"]:
        if len(push_rules["orgs"]["OR"] & {event.orgc_id}) == 0:
            return False

    if "orgs" in push_rules and "NOT" in push_rules["orgs"]:
        if len(push_rules["tag"]["NOT"] & {event.orgc_id}) != 0:
            return False
    return True


def __allowed_by_distribution(event: MispEvent, sharing_groups: list[MispSharingGroup], server: MispServer) -> bool:
    """
    This function checks whether the push of the event-sightings is allowed by the distribution of the event.
    :param event: The event to check.
    :param sharing_groups: The sharing groups of the local server.
    :param server: The remote server.
    :return: Whether the event-sightings are allowed by the distribution of the event.
    """
    if not server.internal or push_worker.push_config.misp_host_org_id != server.remote_org_id:
        if event.distribution < 2:
            return False
    if event.distribution == 4:
        sharing_group: MispSharingGroup = __get_sharing_group(event.sharing_group_id, sharing_groups)
        return __server_in_sg(sharing_group, server)


def __get_sharing_group(sharing_group_id: int, sharing_groups: list[MispSharingGroup]) -> MispSharingGroup:
    """
    This function gets the sharing group with the given id from the list of sharing groups.
    :param sharing_group_id: The id of the sharing group to get.
    :param sharing_groups: The list of sharing groups to get the sharing group from.
    :return: The sharing group with the given id.
    """
    for sharing_group in sharing_groups:
        if sharing_group.id == sharing_group_id:
            return sharing_group
    return None


# <----------

# Helper functions ----------->

def __server_in_sg(sharing_group: MispSharingGroup, server: MispServer) -> bool:
    """
    This function checks whether the server is in the sharing group.
    :param sharing_group: The sharing group to check.
    :param server: The server to check.
    :return: Whether the server is in the sharing group.
    """
    if not sharing_group.roaming:
        cond = False
        for server in sharing_group.sharing_group_servers:
            if server.server_id == server.server_id:
                if server.all_orgs:
                    return True
                else:
                    cond = True
        if not cond and server.internal:
            return False

    for org in sharing_group.sharing_group_orgs:
        if org.org_id == server.remote_org_id:
            return True
    return False

# <----------
