from typing import List, Dict
from uuid import UUID

from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings, ServerNotReachable
from mmisp.worker.jobs.sync.push.job_data import PushData, PushResult, PushTechniqueEnum
from mmisp.worker.misp_database.misp_api import JsonType
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.jobs.sync.push.push_worker import push_worker
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
import re

from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship


@celery_app.task
def push_job(user_data: UserData, push_data: PushData) -> PushResult:
    server_id: int = push_data.server_id
    technique: PushTechniqueEnum = push_data.technique

    if not push_worker.misp_api.is_server_reachable(server_id):
        raise ServerNotReachable(f"Server with id {server_id} server_id doesnt exist")

    remote_server_settings: MispServer = push_worker.misp_api.get_server_settings(server_id)
    server_version: MispServerVersion = push_worker.misp_api.get_server_version(server_id)

    if (not remote_server_settings.push or not server_version.perm_sync
            and not server_version.perm_sighting):
        raise ForbiddenByServerSettings('Remote instance is outdated or no permission to push.')

    pushed_clusters: int = 0
    pushed_events: int = 0
    pushed_proposals: int = 0
    # check whether server allows push
    if remote_server_settings.push and server_version.perm_sync:
        if remote_server_settings.push_galaxy_clusters:
            pushed_clusters = __push_clusters(user_data.user_id, server_id, technique)
        pushed_events = __push_events(user_data.user_id, server_id, technique)
        pushed_proposals = __push_proposals(server_id)

    if remote_server_settings.push_sightings and server_version.perm_sighting:
        __push_sightings(server_id)
        pass
    return PushResult(succes=True)


def __push_clusters(user_id: int, server_id: int, technique: str) -> int:
    clusters: List[MispGalaxyCluster] = push_worker.misp_sql.get_galaxy_clusters("")
    clusters = __remove_older_clusters(clusters, server_id)
    cluster_succes: int = 0
    for cluster in clusters:
        succes: bool = push_worker.misp_api.save_cluster(cluster, server_id)
        if succes:
            cluster_succes += 1
    return cluster_succes

    # event_ids: List[int] = __get_event_ids_to_push(user_id, server_id)
    # for event_id in event_ids:
    #     event: MispEvent = __fetch_event(user_id, event_id)
    #     if __push_event_cluster_to_server(event):
    #         event_clusters: List[MispGalaxyCluster] = __get_elligible_event_clusters_to_push(user_id, event)
    #         for cluster in event_clusters:
    #             result: bool = push_worker.misp_api.upload_cluster_to_server(user_id, server_id, cluster)
    #
    #     result: bool = push_worker.misp_api.upload_event_to_server(event, server_id)

    # __update_last_pushed()


def __remove_older_clusters(clusters: list[MispGalaxyCluster], server_id: int) -> list[MispGalaxyCluster]:
    conditions: JsonType = {"published": True, "minimal": True, "custom": True, "uuid": clusters}
    remote_clusters: list[MispGalaxyCluster] = (
        push_worker.misp_api.get_custom_cluster_from_server(conditions, server_id))
    remote_clusters_dict: dict[UUID, MispGalaxyCluster] = {cluster.uuid: cluster for cluster in remote_clusters}
    out: list[MispGalaxyCluster] = []
    for cluster in clusters:
        if cluster.uuid in remote_clusters_dict and remote_clusters_dict[cluster.uuid].version <= cluster.version:
            out.append(cluster)
    return remote_clusters


def __push_events(user_id: int, server_id: int, technique: str) -> int:
    sharing_groups: list[MispSharingGroup] = push_worker.misp_sql.get_sharing_groups()
    server_sharing_group_ids: list[int] = []
    server: MispServer = push_worker.misp_api.get_server_settings(server_id)
    for sharing_group in sharing_groups:
        if not __server_in_sg(sharing_group, server):
            server_sharing_group_ids.append(sharing_group.id)

    event_sql_query = __generate_event_sql_query(server_sharing_group_ids, technique)
    event_uuids: List[UUID] = push_worker.misp_sql.get_event_uuids(event_sql_query)
    event_uuids = push_worker.misp_api.filter_event_ids_for_push(event_uuids, server_id)
    pushed_events: int = 0
    for event_uuid in event_uuids:
        if __push_event(event_uuid, server_id):
            pushed_events += 1
    return pushed_events


def __generate_event_sql_query(server_sharing_group_ids: list[int], technique: PushTechniqueEnum,
                               server: MispServer) -> str:
    technique_query: str = ""
    if technique == PushTechniqueEnum.INCREMENTAL:
        technique_query = f"id > {server.lastpushedid} AND"
    table_name: str = "?????IDK?????"
    event_reported_query: str = f"'EXISTS (SELECT id, deleted FROM {table_name} WHERE {table_name}.event_id = Event.id and {table_name}.deleted = 0)"
    query: str = technique_query + (f" AND published = 1 AND (attribute_count > 0 OR {event_reported_query}) AND "
                                    f"(distribution > 0 AND distribution < 4 OR distribution = 4 AND sharing_group_id IN "
                                    f"{tuple(server_sharing_group_ids)})")
    return query


def __push_event(event_uuid: UUID, server_version: MispServerVersion, server: MispServer,
                 technique: PushTechniqueEnum) -> bool:
    event: MispEvent = push_worker.misp_api.get_event(event_uuid)
    if server_version.perm_galaxy_editor and server.push_galaxy_clusters and technique == PushTechniqueEnum.FULL:
        __push_event_cluster_to_server(event, server)
    return push_worker.misp_api.save_event(event, server.id)


def __server_in_sg(sharing_group: MispSharingGroup, server: MispServer) -> bool:
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


def __get_event_ids_to_push(user_id: int, server_id: int) -> List[int]:
    # using sharing_group id for fetch_event_ids
    sharing_group_ids = push_worker.misp_api.get_sharing_groups_ids(-1)
    event_ids: List[int] = push_worker.misp_sql.get_event_ids("")
    return push_worker.misp_sql.filter_event_ids_for_push(event_ids, server_id)


def __fetch_event(user_id: int, event_id: int) -> MispEvent:
    param: str = ""
    return push_worker.misp_sql.fetch_event(user_id, param)


def __push_event_cluster_to_server(event: MispEvent, user_id: int, server: MispServer) -> bool:
    tags: list[tuple[MispTag, EventTagRelationship]] = event.tags
    tag_names: list[str] = [tag[0].name for tag in tags]
    custom_cluster_tags: list[str] = list(filter(__is_custom_cluster_tag, tag_names))
    query: str = f"tag_name IN {tuple(custom_cluster_tags)}"
    clusters: list[MispGalaxyCluster] = push_worker.misp_sql.get_galaxy_clusters(query)
    clusters = __remove_older_clusters(clusters, server.id)
    cluster_succes: int = 0
    for cluster in clusters:
        succes: bool = push_worker.misp_api.save_cluster(cluster, server.id)
        if succes:
            cluster_succes += 1
    return cluster_succes


def __push_proposals(server_id: int) -> int:
    local_event_uuids = push_worker.misp_sql.get_event_uuids("")
    event_uuids: list[UUID] = __get_event_views_from_server(True, local_event_uuids, server_id)
    out: int = 0
    for event_uuid in event_uuids:
        event: MispEvent = push_worker.misp_api.get_event(event_uuid)
        if push_worker.misp_api.save_proposal(event):
            out += 1
    return out


def __is_custom_cluster_tag(tag: str) -> bool:
    regex: str = '/misp-galaxy:[^:="]+="[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"/i'
    return re.match(regex, tag) is not None


def __push_sightings(server_id: int) -> int:
    remote_event_views: list[MispEvent] = __get_event_views_from_server(True, [], server_id)
    local_event_uuids: list[UUID] = push_worker.misp_sql.get_event_uuids("")
    local_event_ids_dic: dict[UUID, MispEvent] = __get_local_events_dic(local_event_uuids)
    local_events: list[MispEvent] = [push_worker.misp_sql.get_event(local_event_uuid) for local_event_uuid in
                                     local_event_uuids]

    target_event_uuids: list[UUID] = []
    for remote_event_view in remote_event_views:
        uuid: UUID = remote_event_view.uuid
        if uuid in local_event_ids_dic and local_event_ids_dic[uuid].timestamp > remote_event_view.timestamp:
            target_event_uuids.append(uuid)

    succes: int = 0
    for event_uuid in target_event_uuids:
        event: MispEvent = push_worker.misp_api.get_event(event_uuid)
        if not __allowed_by_push_rules(event, server_id):
            continue
        if not __allowed_by_distribution(event, server_id):
            continue

        remote_sight_uuids: set[UUID] = __get_remote_sightings_uuids(event)
        local_sight_uuids: set[UUID] = __get_local_sightings_uuids(event)
        new_sig_uuids: set[UUID] = local_sight_uuids - remote_sight_uuids

        if len(new_sig_uuids) == 0:
            continue

        new_sightings: list[MispSighting] = [push_worker.misp_sql.get_sighting(new_sig_uuid) for new_sig_uuid in new_sig_uuids]
        succes += push_worker.misp_api.save_sightings(new_sightings, server_id)
    return succes


def __allowed_by_push_rules(event: MispEvent, server: MispServer) -> bool:
    push_rules: Dict[str, Dict[str, set[str]]] = server.push_rules
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


def __allowed_by_distribution(event: MispEvent, server: MispServer) -> bool:
    if not server.internal or push_worker.push_config.misp_host_org_id != server.remote_org_id:
        if event.distribution < 2:
            return False
    if event.distribution == 4:
        sharing_group: MispSharingGroup = push_worker.misp_api.get_sharing_group(event.sharing_group_id)
        return __server_in_sg(sharing_group, server)


def __get_remote_sightings_uuids(event: MispEvent) -> set[UUID]:
    pass


def __get_local_sightings_uuids(event: MispEvent) -> set[UUID]:
    pass


# Move it Up

def __get_event_views_from_server(ignore_filter_rules: bool, local_event_uuids: List[UUID], server_id: int) -> list[
    MispEvent]:
    use_event_blocklist: bool = push_worker.push_config.use_event_blocklist
    use_org_blocklist: bool = push_worker.push_config.use_org_blocklist
    local_event_ids_dic: dict[UUID, MispEvent] = __get_local_events_dic(local_event_uuids)

    remote_event_views: list[MispEvent] = push_worker.misp_api.get_event_views_from_server(ignore_filter_rules,
                                                                                           server_id)
    remote_event_views = push_worker.misp_sql.filter_blocked_events(remote_event_views, use_event_blocklist,
                                                                    use_org_blocklist)
    remote_event_views = __filter_old_events(local_event_ids_dic, remote_event_views, server_id)
    remote_event_views = __filter_empty_events(remote_event_views)

    return remote_event_views


def __filter_old_events(local_event_ids_dic, events) -> List[MispEvent]:
    out: List[MispEvent] = []
    for event in events:
        if (event.uuid in local_event_ids_dic and not event.timestamp <= local_event_ids_dic[event.uuid].timestamp
                and not local_event_ids_dic[event.uuid].locked):
            out.append(event)
    return out


def __filter_empty_events(events: list[MispEvent]) -> list[MispEvent]:
    pass


def __get_local_events_dic(local_event_ids: list[UUID]) -> dict[UUID, MispEvent]:
    out: dict[UUID, MispEvent] = {}
    for event_id in local_event_ids:
        event: MispEvent = push_worker.misp_api.get_event(event_id)
        out[event.uuid] = event
    return out
