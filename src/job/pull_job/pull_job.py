from typing import Dict, List

from src.job.exception.forbidden_by_server_settings import ForbiddenByServerSettings
from src.job.exception.server_not_reachable import ServerNotReachable
from src.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from src.misp_dataclasses.misp_proposal import MispProposal
from src.misp_dataclasses.misp_server import MispServer

from src.job.job import Job
from celery.utils.log import get_task_logger
from src.misp_database.misp_api import JsonType
from src.misp_dataclasses.misp_sighting import MispSighting

logger = get_task_logger("tasks")


class PullJob(Job):

    def run(self, job_id: int, user_id: int, server_id: int, technique: str) -> str:
        logger.info(f"Started Pull Job, id: job_id")
        if not self._misp_api.is_server_reachable(server_id):
            raise ServerNotReachable(f"Server with id: server_id doesnt exist")

        pulled_clusters: int = 0
        remote_server_settings: MispServer = self._misp_api.get_server_settings(server_id)
        if not remote_server_settings.pull:
            raise ForbiddenByServerSettings("")

        if remote_server_settings.pull_galaxy_clusters:
            # job status should be set here
            cluster_ids: List[int] = self.__get_cluster_id_list_based_on_pull_technique(user_id, technique)

            for cluster_id in cluster_ids:
                # add error-handling here
                cluster: MispGalaxyCluster = self._misp_api.fetch_galaxy_cluster(server_id, cluster_id, user_id)
                success: bool = self._misp_api.save_cluster(-1, cluster)
                if success:
                    pulled_clusters += 1

        # job status should be set here
        event_ids: List[int] = self.__get_event_id_list_based_on_pull_technique(technique, False)

        pulled_events: int = 0
        # job status should be set here
        for event_id in event_ids:
            success: bool = self.__pull_event(event_id, user_id, job_id, False)
            if success:
                pulled_events += 1
        failed_pulled_events = len(event_ids) - pulled_events

        pulled_proposals: int = 0
        pulled_sightings: int = 0
        if technique == "full" or technique == 'update':
            fetched_proposals: List[MispProposal] = self._misp_api.fetch_proposals(user_id, server_id)
            for proposal in fetched_proposals:
                success: bool = self._misp_api.save_proposal(proposal)
                if success:
                    pulled_proposals += 1
            # job status should be set here
        
            fetched_sightings: List[MispSighting] = self._misp_api.fetch_sightings(user_id, server_id)
            for sighting in fetched_sightings:
                success: bool = self._misp_api.save_sightings(sighting)
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
        pass

    def __pull_event(self, event_id, user_id, server_id, job_id, param) -> bool:
        event: JsonType = self._misp_api.fetch_event(event_id)
        self._misp_api.save_event(event)
        return True