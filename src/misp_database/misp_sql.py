from typing import List

from src.misp_database.misp_api import JsonType
from src.misp_dataclasses.misp_correlation import MispCorrelation
from src.misp_dataclasses.misp_event import MispEvent
from src.misp_dataclasses.misp_attribute import MispEventAttribute
from src.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from src.misp_dataclasses.misp_post import MispPost
from src.misp_dataclasses.misp_thread import MispThread
from src.misp_dataclasses.misp_user import MispUser


class MispSQL:
    def fetch_galaxy_clusters(self, user_id: int, options: JsonType, full: bool = False,
                              include_full_cluster_relationship: bool = False) -> List[MispGalaxyCluster]:
        pass

    def fetch_event_ids(self, find_param: str) -> List[int]:
        pass

    def filter_event_ids_for_push(self, events: List[int], server_id: int) -> List[int]:
        pass

    def fetch_event(self, user_id: int, param: str) -> MispEvent:
        pass

    def is_excluded_correlation(self, value: str) -> bool:
        pass

    def is_over_correlating_value(self, value: str) -> bool:
        pass

    def get_attribute_correlations(self, value: str) -> List[MispEventAttribute]:
        pass

    def add_correlation_value(self, value: str) -> int:
        # überprüfen ob value schon da
        pass

    def add_correlations(self, correlations: List[MispCorrelation]) -> bool:
        # überprüfen ob correlation schon da
        pass

    def get_correlation_values(self) -> List[str]:
        pass

    def get_count_value_correlations(self, value: str) -> int:
        pass

    def get_over_correlating_values(self) -> list[str]:
        pass

    def add_over_correlating_value(self, value: str, count: int) -> bool:
        # überprüfen ob correlation schon da
        pass

    def delete_over_correlating_value(self, value: str) -> bool:
        pass

    def delete_correlations(self, value: str) -> bool:
        pass

    def get_excluded_correlations(self) -> list[str]:
        pass

    def get_users_in_org(self, org_id: str) -> list[MispUser]:
        pass

    def get_thread(self, thread_id: str) -> MispThread:
        pass

    def get_post(self, post_id: str) -> MispPost:
        pass
