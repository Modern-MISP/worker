from typing import List

from src.exceptions.forbidden_by_server_settings import ForbiddenByServerSettings
from src.exceptions.invalid_server_version import InvalidServerVersion
from src.job.push_job.job_data import PushDate, PushResult, PushTechniqueEnum
from src.misp_database.misp_api import JsonType
from src.misp_dataclasses.misp_event import MispEvent
from src.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from src.job.job import Job
from src.misp_dataclasses.misp_server import MispServer
from src.misp_dataclasses.misp_server_version import MispServerVersion


class PushJob(Job):
    def run(self, user_id: int, push_data: PushDate) -> PushResult:
        server_id: int = push_data.server_id
        technique: PushTechniqueEnum = push_data.technique
        # check Server version comp.

        remote_server_settings: MispServer = self._misp_api.get_server_settings(-1)
        if not remote_server_settings.push:
            raise ForbiddenByServerSettings("")

        version: MispServerVersion = self._misp_api.get_server_version(-1)
        if version.version != "dsf":
            raise InvalidServerVersion()

        # check whether server allows push
        self.__sync_clusters(user_id, server_id, technique)
        return ""

    def __sync_clusters(self, user_id: int, server_id: int, technique: str):
        clusters: List[MispGalaxyCluster] = self.__get_elligible_clusters_to_push(user_id)
        cluster_succes: int = 0
        for cluster in clusters:
            succes: bool = self._misp_api.push_cluster(user_id, cluster)
            if succes:
                cluster_succes += 1
        event_ids: List[int] = self.__get_event_ids_to_push(user_id, server_id)
        for event_id in event_ids:
            event: MispEvent = self.__fetch_event(user_id, event_id)
            if self.__push_event_cluster_to_server(event):
                event_clusters: List[MispGalaxyCluster] = self.__get_elligible_event_clusters_to_push(user_id, event)
                for cluster in event_clusters:
                    result: bool = self._misp_api.upload_cluster_to_server(user_id, server_id, cluster)

            result: bool = self._misp_api.upload_event_to_server(event, server_id)

        self.__update_last_pushed()

    def __get_elligible_clusters_to_push(self, user_id: int) -> List[MispGalaxyCluster]:
        options: JsonType = {}
        return self._misp_sql.fetch_galaxy_clusters(user_id, options, True)

    def __get_event_ids_to_push(self, user_id: int, server_id: int) -> List[int]:
        # using sharing_group id for fetch_event_ids
        sharing_group_ids = self._misp_api.get_sharing_groups_ids(-1)
        event_ids: List[int] = self._misp_sql.fetch_event_ids("")
        return self._misp_sql.filter_event_ids_for_push(event_ids, server_id)

    def __fetch_event(self, user_id: int, event_id: int) -> MispEvent:
        param: str = ""
        return self._misp_sql.fetch_event(user_id, param)

    def __push_event_cluster_to_server(self, event: MispEvent) -> bool:
        pass

    def __get_elligible_event_clusters_to_push(self, user_id: int, event: MispEvent) -> List[MispGalaxyCluster]:
        options: JsonType = {}
        return self._misp_sql.fetch_galaxy_clusters(user_id, options, True)

    def __update_last_pushed(self) -> None:
        pass
