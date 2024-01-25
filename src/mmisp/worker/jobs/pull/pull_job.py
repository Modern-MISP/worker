from typing import List, Dict
from uuid import UUID

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings, ServerNotReachable
from mmisp.worker.jobs.pull import pull_worker
from mmisp.worker.jobs.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.jobs.pull.pull_config_data import PullConfigData
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_database.mmisp_redis import MMispRedis
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_server import MispServer

from celery.utils.log import get_task_logger
from mmisp.worker.misp_database.misp_api import JsonType, MispAPI
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import MispTag
from mmisp.worker.misp_dataclasses.misp_user import MispUser


@celery_app.task
def pull_job(user_data: UserData, pull_data: PullData) -> PullResult:
    server_id: int = pull_data.server_id
    technique: PullTechniqueEnum = pull_data.technique
    misp_api: MispAPI = pull_worker.misp_api
    misp_sql: MispSQL = pull_worker.misp_sql
    mmisp_redis: MMispRedis = pull_worker.mmisp_redis

    if not misp_api.is_server_reachable(server_id):
        raise ServerNotReachable(f"Server with id: server_id doesnt exist")

    pulled_clusters: int = 0
    remote_server_settings: MispServer = misp_api.get_server_settings(server_id)

    if not remote_server_settings.pull:
        raise ForbiddenByServerSettings("")

    if remote_server_settings.pull_galaxy_clusters:
        # jobs status should be set here
        cluster_ids: List[int] = __get_cluster_id_list_based_on_pull_technique(user_data.user_id, technique)

        for cluster_id in cluster_ids:
            # add error-handling here
            cluster: MispGalaxyCluster = misp_api.get_galaxy_cluster(cluster_id, server_id)
            success: bool = misp_api.save_cluster(cluster, -1)

            if success:
                pulled_clusters += 1

    if technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return PullResult(success=0, fails=0, pulled_proposals=0, pulled_sightings=0, pulled_clusters=pulled_clusters)

    # jobs status should be set here
    event_uuids: List[UUID] = __get_event_uuids_based_on_pull_technique(technique, False)

    pulled_events: int = 0
    # jobs status should be set here
    for event_id in event_uuids:
        success: bool = __pull_event(event_id, user_data.user_id, server_id, "")
        if success:
            pulled_events += 1
    failed_pulled_events: int = len(event_uuids) - pulled_events

    pulled_proposals: int = 0
    pulled_sightings: int = 0
    if technique == PullTechniqueEnum.FULL or technique == PullTechniqueEnum.INCREMENTAL:
        fetched_proposals: List[MispProposal] = misp_api.get_proposals(user_data.user_id, server_id)
        for proposal in fetched_proposals:
            success: bool = misp_sql.save_proposal(proposal)
            if success:
                pulled_proposals += 1
        # jobs status should be set here

        fetched_sightings: List[MispSighting] = misp_api.get_sightings(user_data.user_id, server_id)
        for sighting in fetched_sightings:
            success: bool = misp_sql.save_sighting(sighting)
            if success:
                pulled_sightings += 1
        # jobs status should be set here

    # result: str = (f"{pulled_events} events, {pulled_proposals} proposals, {pulled_sightings} sightings and "
    #               f"{pulled_clusters} galaxy clusters  pulled or updated. {failed_pulled_events} "
    #               f"events failed or didn\'t need an update.")
    return PullResult(success=pulled_events, fails=failed_pulled_events, pulled_proposals=pulled_proposals,
                      pulled_sightings=pulled_sightings, pulled_clusters=pulled_clusters)


def __get_sharing_group_ids(user: MispUser) -> List[int]:
    if user.role.perm_site_admin:
        return pull_worker.misp_api.get_sharing_groups_ids(0)

    sharing_groups: list[MispSharingGroup] = pull_worker.misp_sql.get_sharing_groups()
    out: list[int] = []
    for sharing_group in sharing_groups:
        if sharing_group.org_id == user.org_id:
            sharing_group_server: MispSharingGroupServer = sharing_group.sharing_group_server
            sharing_group_org: MispSharingGroupOrg = sharing_group.sharing_group_org
            if sharing_group_server.all_orgs and sharing_group_server.server_id == 0:
                out.append(sharing_group.id)
            elif sharing_group_org.org_id == user.org_id:
                out.append(sharing_group.id)
    return out


def __get_elligble_local_cluster(user_id) -> list[MispGalaxyCluster]:
    user: MispUser = pull_worker.misp_api.get_user(user_id)
    user_cond: str = ""
    if not user.role.perm_site_admin:
        sharing_ids: list[int] = __get_sharing_group_ids(user)
        user_cond = "org_id = " + str(user.org_id) + ("AND distribution > 0 AND distribution < 4 "
                                                      "AND sharing_group_id IN " + str(tuple(sharing_ids)))
    return pull_worker.misp_sql.get_galaxy_clusters(user_id, user_cond, False, False)


def __get_intersection(local_galaxy_clusters: Dict[UUID, MispGalaxyCluster], clusters: list[MispGalaxyCluster]) \
        -> list[MispGalaxyCluster]:
    out: list[MispGalaxyCluster] = []
    for cluster in clusters:
        for local_cluster in local_galaxy_clusters:
            if cluster.uuid == local_cluster.uuid:
                out.append(cluster)
    return out


def __create_uuid_dic(clusters: list[MispGalaxyCluster]) -> Dict[UUID, MispGalaxyCluster]:
    out: Dict[UUID, MispGalaxyCluster] = {}
    for cluster in clusters:
        out[cluster.uuid] = cluster
    return out


def __get_local_cluster_uuids_from_server_for_pull(user_id: int, server_id: int) -> list[UUID]:
    local_galaxy_clusters: list[MispGalaxyCluster] = __get_elligble_local_cluster(user_id)
    if len(local_galaxy_clusters) == 0:
        return []
    conditions: JsonType = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[MispGalaxyCluster] = (pull_worker.misp_api.
                                         get_custom_cluster_from_server(conditions, server_id))
    local_uuid_dic: Dict[UUID, MispGalaxyCluster] = __create_uuid_dic(local_galaxy_clusters)
    remote_clusters = __get_intersection(local_uuid_dic, remote_clusters)
    remote_clusters = pull_worker.misp_sql.filter_blocked_clusters(remote_clusters)
    out: list[UUID] = []
    for cluster in remote_clusters:
        if local_uuid_dic[cluster.uuid].version < cluster.version:
            out.append(cluster.uuid)
    return out


def __get_all_clusters_with_uiid(user_id: int, uuids: list[UUID]) -> list[MispGalaxyCluster]:
    conditions: str = "uuid IN " + str(tuple(uuids))
    return pull_worker.misp_sql.get_galaxy_clusters(user_id, conditions, False, False)


def __get_all_cluster_uuids_from_server_for_pull(user_id: int, server_id: int) -> list[UUID]:
    conditions: JsonType = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[MispGalaxyCluster] = (pull_worker.misp_api.
                                         get_custom_cluster_from_server(conditions, server_id))
    remote_clusters = pull_worker.misp_sql.filter_blocked_clusters(remote_clusters)

    local_galaxy_clusters: list[MispGalaxyCluster] = __get_all_clusters_with_uiid([cluster.uuid for cluster in remote_clusters])
    local_uuid_dic: Dict[UUID, MispGalaxyCluster] = __create_uuid_dic(local_galaxy_clusters)
    out: list[UUID] = []
    for cluster in remote_clusters:
        if local_uuid_dic[cluster.uuid].version < cluster.version:
            out.append(cluster.uuid)
    return out


def __get_cluster_id_list_based_on_pull_technique(user_id: int, technique: PullTechniqueEnum, server_id: int) -> List[UUID]:
    if technique == PullTechniqueEnum.INCREMENTAL or technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return __get_local_cluster_uuids_from_server_for_pull(user_id, server_id)
        pass
    # elif technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
    #     tags: list[MispTag] = pull_worker.misp_sql.get_tags("is_custom_galaxy_cluster = true")
    #
    #     pass
    else:
        return __get_all_cluster_uuids_from_server_for_pull(user_id, server_id)


def __filter_old_events(local_event_ids_dic, events) -> List[MispEvent]:
    out: List[MispEvent] = []
    for event in events:
        if not (event.uuid in local_event_ids_dic and event.timestamp <= local_event_ids_dic[event.uuid].timestamp
                or local_event_ids_dic[event.uuid].locked):
            out.append(event)
    return out


def __filter_empty_events(events: list[MispEvent]) -> list[MispEvent]:
    pass


def __get_event_uuids_based_on_pull_technique(user_id: int, technique: PullTechniqueEnum, server_id: int) -> List[UUID]:
    local_event_uuids: List[UUID] = pull_worker.misp_sql.get_event_uuids("")
    if technique == PullTechniqueEnum.FULL:
        return __get_event_uuids_from_server(False, local_event_uuids, server_id)
    elif technique == PullTechniqueEnum.INCREMENTAL:
        remote_event_ids: List[UUID] = __get_event_uuids_from_server(True, local_event_uuids, server_id)
        return list(set(local_event_uuids) & set(remote_event_ids))
    else:
        return []


def __get_event_uuids_from_server(ignore_filter_rules: bool, local_event_uuids: List[UUID], server_id: int) -> list[UUID]:
    use_event_blocklist: bool = pull_worker.pull_config.use_event_blocklist
    use_org_blocklist: bool = pull_worker.pull_config.use_org_blocklist
    local_event_ids_dic: dict[UUID, MispEvent] = __get_local_events(local_event_uuids)

    event_views: list[MispEvent] = pull_worker.misp_api.get_event_views_from_server(ignore_filter_rules, server_id)
    event_views = pull_worker.misp_sql.filter_blocked_events(event_views, use_event_blocklist, use_org_blocklist)
    event_views = __filter_old_events(local_event_ids_dic, event_views, server_id)
    event_views = __filter_empty_events(event_views)

    event_uuids: list[UUID] = []
    for event in event_views:
        event_uuids.append(event.uuid)
    return event_uuids


def __get_local_events(local_event_ids: list[UUID]) -> dict[UUID, MispEvent]:
    out: dict[UUID, MispEvent] = {}
    for event_id in local_event_ids:
        event: MispEvent = pull_worker.misp_api.get_event(event_id)
        out[event.uuid] = event
    return out


def __pull_event(event_id, user_id, server_id, param) -> bool:
    event: JsonType = pull_worker.misp_api.fetch_event(event_id)
    pull_worker.misp_api.save_event(event)
    return True
