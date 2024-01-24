from typing import List
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings, InvalidServerVersion
from mmisp.worker.jobs.push.job_data import PushData, PushResult, PushTechniqueEnum
from mmisp.worker.misp_database.misp_api import JsonType
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.jobs.push.push_worker import push_worker
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion


@celery_app.task
def push_job(user_data: UserData, push_data: PushData) -> PushResult:
    server_id: int = push_data.server_id
    technique: PushTechniqueEnum = push_data.technique
    # check Server version comp.

    remote_server_settings: MispServer = push_worker.misp_api.get_server_settings(-1)
    if not remote_server_settings.push:
        raise ForbiddenByServerSettings("")

    version: MispServerVersion = push_worker.misp_api.get_server_version(-1)
    if version.version != "dsf":
        raise InvalidServerVersion()

    # check whether server allows push
    __sync_clusters(user_data.user_id, server_id, technique)
    return ""


def __sync_clusters(user_id: int, server_id: int, technique: str):
    clusters: List[MispGalaxyCluster] = __get_elligible_clusters_to_push(user_id)
    cluster_succes: int = 0
    for cluster in clusters:
        succes: bool = push_worker.misp_api.push_cluster(user_id, cluster)
        if succes:
            cluster_succes += 1
    event_ids: List[int] = __get_event_ids_to_push(user_id, server_id)
    for event_id in event_ids:
        event: MispEvent = __fetch_event(user_id, event_id)
        if __push_event_cluster_to_server(event):
            event_clusters: List[MispGalaxyCluster] = __get_elligible_event_clusters_to_push(user_id, event)
            for cluster in event_clusters:
                result: bool = push_worker.misp_api.upload_cluster_to_server(user_id, server_id, cluster)

        result: bool = push_worker.misp_api.upload_event_to_server(event, server_id)

    __update_last_pushed()


def __get_elligible_clusters_to_push(user_id: int) -> List[MispGalaxyCluster]:
    options: JsonType = {}
    return push_worker.misp_sql.fetch_galaxy_clusters(user_id, options, True)


def __get_event_ids_to_push(user_id: int, server_id: int) -> List[int]:
    # using sharing_group id for fetch_event_ids
    sharing_group_ids = push_worker.misp_api.get_sharing_groups_ids(-1)
    event_ids: List[int] = push_worker.misp_sql.fetch_event_ids("")
    return push_worker.misp_sql.filter_event_ids_for_push(event_ids, server_id)


def __fetch_event(user_id: int, event_id: int) -> MispEvent:
    param: str = ""
    return push_worker.misp_sql.fetch_event(user_id, param)


def __push_event_cluster_to_server(event: MispEvent) -> bool:
    pass


def __get_elligible_event_clusters_to_push(user_id: int, event: MispEvent) -> List[MispGalaxyCluster]:
    options: JsonType = {}
    return push_worker.misp_sql.fetch_galaxy_clusters(user_id, options, True)


def __update_last_pushed() -> None:
    pass
