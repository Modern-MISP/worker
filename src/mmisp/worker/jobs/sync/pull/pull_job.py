from celery.utils.log import get_task_logger

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings, ServerNotReachable
from mmisp.worker.jobs.sync.pull.pull_worker import pull_worker
from mmisp.worker.jobs.sync.pull.job_data import PullData, PullResult, PullTechniqueEnum
from mmisp.worker.jobs.sync.sync_helper import _filter_old_events, _get_local_events_dic, \
    _get_mini_events_from_server
from mmisp.worker.misp_dataclasses.misp_event_view import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_server import MispServer

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_user import MispUser

JOB_NAME = "pull_job"
__logger = get_task_logger(JOB_NAME)


@celery_app.task
def test_pull_job(user_data: UserData, pull_data: PullData) -> PullResult:
    """
    This function represents the pull job. It pulls data from a remote server and saves it in the local server.
    :param user_data: The user data of the user who started the job.
    :param pull_data: The data needed to pull the data from the remote server.
    :return: An object containing the results of the pull job.
    """

    server_id: int = pull_data.server_id
    technique: PullTechniqueEnum = pull_data.technique
    remote_server: MispServer = pull_worker.misp_api.get_server(server_id)

    if not remote_server.pull:
        raise ForbiddenByServerSettings(f"Pulling from Server with id {remote_server.id} is not allowed.")

    user: MispUser = pull_worker.misp_api.get_user(user_data.user_id)
    pulled_clusters: int = 0
    if remote_server.pull_galaxy_clusters:
        pulled_clusters = __pull_clusters(user, technique, remote_server)
        __logger.info(f"{pulled_clusters} galaxy clusters pulled or updated.")

    if technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return PullResult(successes=0, fails=0, pulled_proposals=0, pulled_sightings=0, pulled_clusters=pulled_clusters)


    pull_event_return: tuple[int, int] = __pull_events(user, technique, remote_server)
    pulled_events: int = pull_event_return[0]
    failed_pulled_events: int = pull_event_return[1]
    __logger.info(f"{pulled_events} events pulled or updated.")
    __logger.info(f"{failed_pulled_events} events failed or didn\'t need an update.")

    pulled_proposals: int = 0
    pulled_sightings: int = 0
    if technique == PullTechniqueEnum.FULL or technique == PullTechniqueEnum.INCREMENTAL:
        pulled_proposals = __pull_proposals(user, remote_server)
        __logger.info(f"{pulled_proposals} proposals pulled or updated.")
        pulled_sightings = __pull_sightings(remote_server)
        __logger.info(f"{pulled_sightings} sightings pulled or updated.")
    return PullResult(successes=pulled_events, fails=failed_pulled_events, pulled_proposals=pulled_proposals,
                      pulled_sightings=pulled_sightings, pulled_clusters=pulled_clusters)


# Functions designed to help with the Galaxy Cluster push ----------->

def __pull_clusters(user: MispUser, technique: PullTechniqueEnum, remote_server: MispServer) -> int:
    """
    This function pulls the galaxy clusters from the remote server and saves them in the local server.
    :param user: The user who started the job.
    :param technique: The technique used to pull the galaxy clusters.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: The number of pulled galaxy clusters.
    """

    pulled_clusters: int = 0
    cluster_ids: list[int] = __get_cluster_id_list_based_on_pull_technique(user, technique, remote_server)

    for cluster_id in cluster_ids:
        try:
            cluster: MispGalaxyCluster = pull_worker.misp_api.get_galaxy_cluster(cluster_id, remote_server)
            if pull_worker.misp_api.save_cluster(cluster):
                pulled_clusters += 1
            else:
                __logger.info(f"Cluster with id {cluster_id} already exists and is up to date.")
        except Exception as e:
            __logger.warning(f"Error while pulling galaxy cluster with id {cluster_id}, "
                           f"from Server with id {remote_server.id}: " + str(e))
    return pulled_clusters


def __get_cluster_id_list_based_on_pull_technique(user: MispUser, technique: PullTechniqueEnum,
                                                  remote_server: MispServer) -> list[int]:
    """
    This function returns a list of galaxy cluster ids based on the pull technique.
    :param user: The user who started the job.
    :param technique: The technique used to pull the galaxy clusters.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster ids.
    """
    if technique == PullTechniqueEnum.INCREMENTAL or technique == PullTechniqueEnum.PULL_RELEVANT_CLUSTERS:
        return __get_local_cluster_ids_from_server_for_pull(user, remote_server)
    else:
        return __get_all_cluster_ids_from_server_for_pull(user, remote_server)


def __get_local_cluster_ids_from_server_for_pull(user: MispUser, remote_server: MispServer) -> list[int]:
    """
    This function returns a list of galaxy cluster ids, from the locale server, based on the pull technique.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster ids.
    """

    local_galaxy_clusters: list[MispGalaxyCluster] = __get_accessible_local_cluster(user)
    if len(local_galaxy_clusters) == 0:
        return []
    conditions: dict = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[MispGalaxyCluster] = (pull_worker.misp_api.
                                                get_custom_clusters(conditions, remote_server))
    local_id_dic: dict[int, MispGalaxyCluster] = {cluster.id: cluster for cluster in local_galaxy_clusters}
    remote_clusters = __get_intersection(local_id_dic, remote_clusters)
    remote_clusters = pull_worker.misp_sql.filter_blocked_clusters(remote_clusters)
    out: list[int] = []
    for cluster in remote_clusters:
        if local_id_dic[cluster.id].version < cluster.version:
            out.append(cluster.id)
    return out


def __get_all_cluster_ids_from_server_for_pull(user: MispUser, remote_server: MispServer) -> list[int]:
    """
    This function returns a list of galaxy cluster ids, from the remote server, based on the pull technique.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the galaxy clusters are pulled.
    :return: A list of galaxy cluster ids.
    """

    conditions: dict = {"published": True, "minimal": True, "custom": True}
    remote_clusters: list[MispGalaxyCluster] = (pull_worker.misp_api.
                                                get_custom_clusters(conditions, remote_server))
    remote_clusters = pull_worker.misp_sql.filter_blocked_clusters(remote_clusters)

    local_galaxy_clusters: list[MispGalaxyCluster] = __get_all_clusters_with_id([cluster.id for cluster in
                                                                                 remote_clusters])
    local_id_dic: dict[int, MispGalaxyCluster] = {cluster.id: cluster for cluster in local_galaxy_clusters}
    out: list[int] = []
    for cluster in remote_clusters:
        if local_id_dic[cluster.int].version < cluster.version:
            out.append(cluster.int)
    return out


def __get_accessible_local_cluster(user: MispUser) -> list[MispGalaxyCluster]:
    """
    This function returns a list of galaxy clusters that the user has access to.
    :param user: The user who started the job.
    :return: A list of galaxy clusters.
    """

    conditions: dict = {"published": True, "minimal": True, "custom": True}
    local_galaxy_clusters: list[MispGalaxyCluster] = pull_worker.misp_api.get_custom_clusters(conditions)

    if not user.role.perm_site_admin:
        sharing_ids: list[int] = __get_sharing_group_ids_of_user(user)
        out: list[MispGalaxyCluster] = []
        for cluster in local_galaxy_clusters:
            if (cluster.organisation.id == user.org_id and 0 < cluster.distribution < 4 and
                    cluster.sharing_group_id in sharing_ids):
                out.append(cluster)
        return out

    return local_galaxy_clusters


def __get_all_clusters_with_id(ids: list[int]) -> list[MispGalaxyCluster]:
    """
    This function returns a list of galaxy clusters with the given ids.
    :param ids: The ids of the galaxy clusters.
    :return: A list of galaxy clusters.
    """
    out: list[MispGalaxyCluster] = []
    for cluster_id in ids:
        try:
            out.append(pull_worker.misp_api.get_galaxy_cluster(cluster_id))
        except Exception as e:
            __logger.warning(f"Error while getting galaxy cluster, with id {cluster_id}, from own Server: " + str(e))
            pass

    return out


def __get_sharing_group_ids_of_user(user: MispUser) -> list[int]:
    """
    This function returns a list of sharing group ids that the user has access to.
    :param user: The user who started the job.
    :return: A list of sharing group ids.
    """

    sharing_groups: list[MispSharingGroup] = pull_worker.misp_api.get_sharing_groups()
    if user.role.perm_site_admin:
        return [sharing_group.id for sharing_group in sharing_groups]

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
    """
    This function pulls the events from the remote server and saves them in the local server.
    :param user: The user who started the job.
    :param technique: The technique used to pull the events.
    :param remote_server: The remote server from which the events are pulled.
    :return: The number of pulled events and the number of failed pulled events.
    """

    pulled_events: int = 0
    remote_event_ids: list[int] = __get_event_ids_based_on_pull_technique(technique, remote_server)
    for event_id in remote_event_ids:
        if __pull_event(event_id, remote_server):
            pulled_events += 1
        else:
            __logger.info(f"Event with id {event_id} already exists and is up to date.")
    failed_pulled_events: int = len(remote_event_ids) - pulled_events
    return pulled_events, failed_pulled_events


def __get_event_ids_based_on_pull_technique(technique: PullTechniqueEnum, remote_server: MispServer) \
        -> list[int]:
    """
    This function returns a list of event ids based on the pull technique.
    :param technique: The technique used to pull the events.
    :param remote_server: The remote server from which the events are pulled.
    :return: A list of event ids.
    """
    local_minimal_events: list[MispMinimalEvent] = pull_worker.misp_api.get_minimal_events(True)
    local_event_ids: list[int] = [event.id for event in local_minimal_events]
    if technique == PullTechniqueEnum.FULL:
        return __get_event_ids_from_server(False, local_event_ids, remote_server)
    elif technique == PullTechniqueEnum.INCREMENTAL:
        remote_event_ids: list[int] = __get_event_ids_from_server(True, local_event_ids, remote_server)
        return list(set(local_event_ids) & set(remote_event_ids))
    else:
        return []


def __pull_event(event_id: int, remote_server: MispServer) -> bool:
    """
    This function pulls the event from the remote server and saves it in the local server.
    :param event_id: The id of the event.
    :param remote_server: The remote server from which the event is pulled.
    :return: True if the event was pulled successfully, False otherwise.
    """
    try:
        event: dict = pull_worker.misp_api.get_event_no_parse(event_id, remote_server)
        if not pull_worker.misp_api.save_event_dic(event):
            return pull_worker.misp_api.update_event_dic(event)
        return True
    except Exception as e:
        __logger.warning(f"Error while pulling Event with id {event_id}, "
                       f"from Server with id {remote_server.id}: " + str(e))
        return False


def __get_event_ids_from_server(ignore_filter_rules: bool, local_event_ids: list[int], remote_server: MispServer) -> \
        list[int]:
    """
    This function returns a list of event ids from the remote server.
    :param ignore_filter_rules: If True, the filter rules will be ignored. If False, the filter rules will be applied.
    :param local_event_ids: The ids of the events that are saved in the local server.
    :param remote_server: The remote server from which the event ids are pulled.
    :return: A list of event ids.
    """
    remote_event_views: list[MispMinimalEvent] = _get_mini_events_from_server(ignore_filter_rules, local_event_ids,
                                                                              pull_worker.sync_config,
                                                                              pull_worker.misp_api,
                                                                              pull_worker.misp_sql, remote_server)

    return [event.id for event in remote_event_views]


# <-----------

# Functions designed to help with the Proposal pull ----------->
def __pull_proposals(user: MispUser, remote_server: MispServer) -> int:
    """
    This function pulls the proposals from the remote server and saves them in the local server.
    :param user: The user who started the job.
    :param remote_server: The remote server from which the proposals are pulled.
    :return: The number of pulled proposals.
    """
    fetched_proposals: list[MispProposal] = pull_worker.misp_api.get_proposals(remote_server)
    pulled_proposals: int = 0
    for proposal in fetched_proposals:
        try:
            event: MispEvent = pull_worker.misp_api.get_event(proposal.event_id, remote_server)
            if pull_worker.misp_api.save_proposal(event):
                pulled_proposals += 1
            else:
                __logger.info(f"Proposal with id {proposal.id} already exists and is up to date.")
        except Exception as e:
            __logger.warning(f"Error while pulling Event with id {proposal.event_id}, "
                           f"from Server with id {remote_server.id}: " + str(e))
    return pulled_proposals


# <-----------
# Functions designed to help with the Sighting pull ----------->

def __pull_sightings(remote_server: MispServer) -> int:
    """
    This function pulls the sightings from the remote server and saves them in the local server.
    :param fetched_sightings: The sightings that are pulled from the remote server.
    :return: The number of pulled sightings.
    """

    remote_event_views: list[MispMinimalEvent] = pull_worker.misp_api.get_minimal_events(False,
                                                                                              remote_server)
    remote_events: list[MispEvent] = []
    for event in remote_event_views:
        try:
            remote_events.append(pull_worker.misp_api.get_event(event.id, remote_server))
        except Exception as e:
            __logger.warning(f"Error while pulling Event with id {event.id}, "
                           f"from Server with id {remote_server.id}: " + str(e))
    local_events: list[MispEvent] = []
    for event in remote_events:
        try:
            local_event: MispEvent = pull_worker.misp_api.get_event(event.id, None)
            local_events.append(local_event)
        except Exception as e:
            __logger.warning(f"Error while pulling Event with id {event.id}, "
                           f"from Server with id {remote_server.id}: " + str(e))

    local_event_ids_dic: dict[int, MispEvent] = {event.id: event for event in local_events}

    event_ids: list[int] = []
    for remote_event in remote_event_views:
        if (remote_event.id in local_event_ids_dic and remote_event.timestamp >
                local_event_ids_dic[remote_event.id].timestamp):
            event_ids.append(remote_event.id)

    fetched_sightings: list[MispSighting] = []
    for event_id in event_ids:
        try:
            fetched_sightings.extend(pull_worker.misp_api.get_sightings_from_event(event_id, remote_server))
        except Exception as e:
            __logger.warning(f"Error while pulling Sightings from Event with id {event_id}, "
                           f"from Server with id {remote_server.id}: " + str(e))
            pass

    pulled_sightings: int = 0
    for sighting in fetched_sightings:
        if pull_worker.misp_api.save_sighting(sighting):
            pulled_sightings += 1
        else:
            __logger.info(f"Sighting with id {sighting.id} already exists and is up to date.")
    return pulled_sightings


# <-----------

# Helper functions ----------->

def __get_intersection(cluster_dic: dict[int, MispGalaxyCluster], cluster_list: list[MispGalaxyCluster]) \
        -> list[MispGalaxyCluster]:
    """
    This function returns the intersection of the cluster_dic and the cluster_list.
    :param cluster_dic: A dictionary containing the galaxy clusters.
    :param cluster_list: A list containing the galaxy clusters.
    :return: A list containing the intersection of the cluster_dic and the cluster_list.
    """
    out: list[MispGalaxyCluster] = []
    for cluster in cluster_list:
        for local_cluster_id in cluster_dic:
            if cluster.id == local_cluster_id:
                out.append(cluster)
    return out
# <-----------
