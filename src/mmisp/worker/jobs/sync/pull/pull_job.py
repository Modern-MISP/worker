from typing import List, Dict

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings, ServerNotReachable
from mmisp.worker.jobs.sync.pull.pull_worker import pull_worker
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_server import MispServer

from mmisp.worker.misp_database.misp_api import JsonType, MispAPI
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_user import MispUser


@celery_app.task
def pull_job(user_data: UserData, pull_data: PullData) -> PullResult:
    server_id: int = pull_data.server_id
    technique: PullTechniqueEnum = pull_data.technique
    misp_api: MispAPI = pull_worker.misp_api
    misp_sql: MispSQL = pull_worker.misp_sql

    server: MispServer = misp_api.get_server(server_id)
    if not misp_api.is_server_reachable(server):
        raise ServerNotReachable(f"Server with id: server_id doesnt exist")

    remote_server: MispServer = misp_api.get_server(server_id)

    if not remote_server.pull:
        raise ForbiddenByServerSettings("")

    user: MispUser = misp_api.get_user(user_data.user_id)
    pulled_clusters: int = 0
    if remote_server.pull_galaxy_clusters:
        pulled_clusters = __pull_clusters(user, technique, remote_server)

    if technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return PullResult(success=0, fails=0, pulled_proposals=0, pulled_sightings=0, pulled_clusters=pulled_clusters)

    # jobs status should be set here
    pull_event_return: tuple[int, int] = __pull_events(user, technique, remote_server)
    pulled_events: int = pull_event_return[0]
    failed_pulled_events: int = pull_event_return[1]

    pulled_proposals: int = 0
    pulled_sightings: int = 0
    if technique == PullTechniqueEnum.FULL or technique == PullTechniqueEnum.INCREMENTAL:
        pulled_proposals = __pull_proposals(user, remote_server)

        fetched_sightings: List[MispSighting] = misp_api.get_sightings(user_data.user_id, remote_server)
        pulled_sightings = __pull_sightings(fetched_sightings)

    # result: str = (f"{pulled_events} events, {pulled_proposals} proposals, {pulled_sightings} sightings and "
    #               f"{pulled_clusters} galaxy clusters  pulled or updated. {failed_pulled_events} "
    #               f"events failed or didn\'t need an update.")
    return PullResult(success=pulled_events, fails=failed_pulled_events, pulled_proposals=pulled_proposals,
                      pulled_sightings=pulled_sightings, pulled_clusters=pulled_clusters)


# Functions designed to help with the Galaxy Cluster push ----------->

def __pull_clusters(user: MispUser, technique: PullTechniqueEnum, remote_server: MispServer) -> int:
    pulled_clusters: int = 0
    # jobs status should be set here
    cluster_ids: List[int] = __get_cluster_id_list_based_on_pull_technique(user, technique, remote_server)

    for cluster_id in cluster_ids:
        # add error-handling here
        cluster: MispGalaxyCluster = pull_worker.misp_api.get_galaxy_cluster(cluster_id, remote_server)
        success: bool = pull_worker.misp_api.save_cluster(cluster, None)

        if success:
            pulled_clusters += 1
    return pulled_clusters


def __get_cluster_id_list_based_on_pull_technique(user: MispUser, technique: PullTechniqueEnum,
                                                  remote_server: MispServer) \
        -> List[int]:
    if technique == PullTechniqueEnum.INCREMENTAL or technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return __get_local_cluster_ids_from_server_for_pull(user, remote_server)
    else:
        return __get_all_cluster_ids_from_server_for_pull(user, remote_server)


def __get_local_cluster_ids_from_server_for_pull(user: MispUser, remote_server: MispServer) -> list[int]:
    local_galaxy_clusters: list[MispGalaxyCluster] = __get_accessible_local_cluster(user)
    if len(local_galaxy_clusters) == 0:
        return []
    conditions: JsonType = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[MispGalaxyCluster] = (pull_worker.misp_api.
                                                get_custom_cluster_from_server(conditions, remote_server))
    local_id_dic: Dict[int, MispGalaxyCluster] = {cluster.id: cluster for cluster in local_galaxy_clusters}
    remote_clusters = __get_intersection(local_id_dic, remote_clusters)
    remote_clusters = pull_worker.misp_sql.filter_blocked_clusters(remote_clusters)
    out: list[int] = []
    for cluster in remote_clusters:
        if local_id_dic[cluster.id].version < cluster.version:
            out.append(cluster.id)
    return out


def __get_all_cluster_ids_from_server_for_pull(user: MispUser, remote_server: MispServer) -> list[int]:
    conditions: JsonType = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[MispGalaxyCluster] = (pull_worker.misp_api.
                                                get_custom_cluster_from_server(conditions, remote_server))
    remote_clusters = pull_worker.misp_sql.filter_blocked_clusters(remote_clusters)

    local_galaxy_clusters: list[MispGalaxyCluster] = __get_all_clusters_with_id(user,
                                                                                [cluster.id for cluster in
                                                                                 remote_clusters])
    local_id_dic: Dict[int, MispGalaxyCluster] = {cluster.id: cluster for cluster in local_galaxy_clusters}
    out: list[int] = []
    for cluster in remote_clusters:
        if local_id_dic[cluster.int].version < cluster.version:
            out.append(cluster.int)
    return out


def __get_accessible_local_cluster(user_id) -> list[MispGalaxyCluster]:
    user: MispUser = pull_worker.misp_api.get_user(user_id)
    user_cond: str = ""
    if not user.role.perm_site_admin:
        sharing_ids: list[int] = __get_sharing_group_ids_of_user(user)
        user_cond = "org_id = " + str(user.org_id) + ("AND distribution > 0 AND distribution < 4 "
                                                      "AND sharing_group_id IN " + str(tuple(sharing_ids)))
    return pull_worker.misp_sql.get_galaxy_clusters(user_cond)


def __get_all_clusters_with_id(user: MispUser, ids: list[int]) -> list[MispGalaxyCluster]:
    conditions: str = "id IN " + str(tuple(ids))
    return pull_worker.misp_sql.get_galaxy_clusters(conditions)


def __get_sharing_group_ids_of_user(user: MispUser) -> List[int]:
    if user.role.perm_site_admin:
        return pull_worker.misp_api.get_sharing_groups_ids(None)

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


# <-----------

# Functions designed to help with the Event pull ----------->


def __pull_events(user: MispUser, technique: PullTechniqueEnum, remote_server: MispServer) -> tuple[int, int]:
    pulled_events: int = 0
    remote_event_ids: List[int] = __get_event_ids_based_on_pull_technique(user, technique, remote_server)
    # jobs status should be set here
    for event_id in remote_event_ids:
        success: bool = __pull_event(event_id, user, remote_server)
        if success:
            pulled_events += 1
    failed_pulled_events: int = len(remote_event_ids) - pulled_events
    return pulled_events, failed_pulled_events


def __get_event_ids_based_on_pull_technique(user: MispUser, technique: PullTechniqueEnum, remote_server: MispServer) -> \
        List[int]:
    local_event_ids: List[int] = pull_worker.misp_sql.get_event_ids("")
    if technique == PullTechniqueEnum.FULL:
        return __get_event_ids_from_server(False, local_event_ids, remote_server)
    elif technique == PullTechniqueEnum.INCREMENTAL:
        remote_event_ids: List[int] = __get_event_ids_from_server(True, local_event_ids, remote_server)
        return list(set(local_event_ids) & set(remote_event_ids))
    else:
        return []


def __pull_event(event_id: int, user: MispUser, remote_server: MispServer) -> bool:
    event: MispEvent = pull_worker.misp_api.get_event_from_server(event_id, remote_server)
    pull_worker.misp_api.save_event(event, None)
    return True


def __get_event_ids_from_server(ignore_filter_rules: bool, local_event_ids: List[int], remote_server: MispServer) -> \
        list[
            int]:
    use_event_blocklist: bool = pull_worker.pull_config.use_event_blocklist
    use_org_blocklist: bool = pull_worker.pull_config.use_org_blocklist
    local_event_ids_dic: dict[int, MispEvent] = __get_local_events(local_event_ids)

    remote_event_views: list[MispEvent] = pull_worker.misp_api.get_event_views_from_server(ignore_filter_rules,
                                                                                           remote_server)
    remote_event_views = pull_worker.misp_sql.filter_blocked_events(remote_event_views, use_event_blocklist,
                                                                    use_org_blocklist)
    remote_event_views = __filter_old_events(local_event_ids_dic, remote_event_views)
    remote_event_views = __filter_empty_events(remote_event_views)

    event_ids: list[int] = []
    for event in remote_event_views:
        event_ids.append(event.id)
    return event_ids


def __get_local_events(local_event_ids: list[int]) -> dict[int, MispEvent]:
    out: dict[int, MispEvent] = {}
    for event_id in local_event_ids:
        event: MispEvent = pull_worker.misp_api.get_event(event_id)
        out[event.id] = event
    return out


def __filter_old_events(local_event_ids_dic: Dict[int, MispEvent], events: list[MispEvent]) -> List[MispEvent]:
    out: List[MispEvent] = []
    for event in events:
        if (event.id in local_event_ids_dic and not event.timestamp <= local_event_ids_dic[event.id].timestamp
                and not local_event_ids_dic[event.id].locked):
            out.append(event)
    return out


def __filter_empty_events(events: list[MispEvent]) -> list[MispEvent]:
    pass


# <-----------

# Functions designed to help with the Proposal pull ----------->
def __pull_proposals(user: MispUser, remote_server: MispServer) -> int:
    fetched_proposals: List[MispProposal] = pull_worker.misp_api.get_proposals(user.user_id, remote_server)
    pulled_proposals: int = 0
    # jobs status should be set here
    for proposal in fetched_proposals:
        success: bool = pull_worker.misp_sql.save_proposal(proposal)
        if success:
            pulled_proposals += 1
    return pulled_proposals


# <-----------
# Functions designed to help with the Sighting pull ----------->

def __pull_sightings(fetched_sightings: list[MispSighting]):
    pulled_sightings: int = 0
    for sighting in fetched_sightings:
        success: bool = pull_worker.misp_sql.save_sighting(sighting)
        if success:
            pulled_sightings += 1
    # jobs status should be set here
    return pulled_sightings


# <-----------

# Helper functions ----------->

def __get_intersection(local_galaxy_clusters: Dict[int, MispGalaxyCluster], clusters: list[MispGalaxyCluster]) \
        -> list[MispGalaxyCluster]:
    out: list[MispGalaxyCluster] = []
    for cluster in clusters:
        for local_cluster_id in local_galaxy_clusters:
            if cluster.id == local_cluster_id:
                out.append(cluster)
    return out
# <-----------
