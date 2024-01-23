from enum import Enum
from typing import List

from src.mmisp.worker.api.job_router.input_data import UserData
from src.mmisp.worker.exceptions.server_exceptions import ForbiddenByServerSettings, ServerNotReachable
from src.mmisp.worker.job.pull_job.job_data import PullDate, PullResult, PullTechniqueEnum
from src.mmisp.worker.job.pull_job.pull_config_data import PullConfigData
from src.mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from src.mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from src.mmisp.worker.misp_dataclasses.misp_server import MispServer

from src.mmisp.worker.job.job import Job
from celery.utils.log import get_task_logger
from src.mmisp.worker.misp_database.misp_api import JsonType
from src.mmisp.worker.misp_dataclasses.misp_sighting import MispSighting

logger = get_task_logger("tasks")


class PullJob(Job):
    def __init__(self):
        super().__init__()
        self.config = PullConfigData()

    def run(self, user_data: UserData, pull_data: PullDate) -> PullResult:
        server_id: int = pull_data.server_id
        technique: PullTechniqueEnum = pull_data.technique
        logger.info(f"Started Pull Job, id: job_id")
        if not self._misp_api.is_server_reachable(server_id):
            raise ServerNotReachable(f"Server with id: server_id doesnt exist")

        pulled_clusters: int = 0
        remote_server_settings: MispServer = self._misp_api.get_server_settings(server_id)
        if not remote_server_settings.pull:
            raise ForbiddenByServerSettings("")

        if remote_server_settings.pull_galaxy_clusters:
            # job status should be set here
            cluster_ids: List[int] = self.__get_cluster_id_list_based_on_pull_technique(user_data.user_id, technique)

            for cluster_id in cluster_ids:
                # add error-handling here
                cluster: MispGalaxyCluster = self._misp_api.fetch_galaxy_cluster(server_id, cluster_id, user_data.user_id)
                success: bool = self._misp_api.save_cluster(-1, cluster)
                if success:
                    pulled_clusters += 1

        # job status should be set here
        event_ids: List[int] = self.__get_event_id_list_based_on_pull_technique(technique, False)

        pulled_events: int = 0
        # job status should be set here
        for event_id in event_ids:
            success: bool = self.__pull_event(event_id, user_data.user_id, False)
            if success:
                pulled_events += 1
        failed_pulled_events = len(event_ids) - pulled_events

        pulled_proposals: int = 0
        pulled_sightings: int = 0
        if technique == "full" or technique == 'update':
            fetched_proposals: List[MispProposal] = self._misp_api.fetch_proposals(user_data.user_id, server_id)
            for proposal in fetched_proposals:
                success: bool = self._misp_api.save_proposal(proposal)
                if success:
                    pulled_proposals += 1
            # job status should be set here

            fetched_sightings: List[MispSighting] = self._misp_api.fetch_sightings(user_data.user_id, server_id)
            for sighting in fetched_sightings:
                success: bool = self._misp_api.save_sighting(sighting)
                if success:
                    pulled_sightings += 1
            # job status should be set here

        result: str = (f"{pulled_events} events, {pulled_proposals} proposals, {pulled_sightings} sightings and "
                       f"{pulled_clusters} galaxy clusters  pulled or updated. {failed_pulled_events} "
                       f"events failed or didn\'t need an update.")
        return result

    def __get_cluster_id_list_based_on_pull_technique(self, user_id, technique) -> List[int]:
        # uses _misp_api.fetchCustomClusterIdsFromServer(conditions)
        pass

    def __get_event_id_list_based_on_pull_technique(self, technique: str, force: bool) -> List[int]:
        # uses _misp_api.get_event_ids_from_server(ignore_filter_rules)
        # uses self._misp_sql.remove_blocked_events(event_ids)
        pass

    def __pull_event(self, event_id, user_id, server_id, param) -> bool:
        event: JsonType = self._misp_api.fetch_event(event_id)
        self._misp_api.save_event(event)
        return True
