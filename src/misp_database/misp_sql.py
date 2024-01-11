
from src.misp_database.misp_api import JsonType
from src.misp_dataclasses.misp_correlation import MispCorrelation
from src.misp_dataclasses.misp_event import MispEvent
from src.misp_dataclasses.misp_attribute import MispEventAttribute
from src.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from src.misp_dataclasses.misp_post import MispPost
from src.misp_dataclasses.misp_sharing_group import MispSharingGroup
from src.misp_dataclasses.misp_sighting import MispSighting
from src.misp_dataclasses.misp_thread import MispThread
from src.misp_dataclasses.misp_user import MispUser


class MispSQL:
    def get_galaxy_clusters(self, user_id: int, options: JsonType, full: bool,
                            include_full_cluster_relationship: bool) -> list[MispGalaxyCluster]:
        pass

    def get_event_ids(self, param: str) -> list[int]:
        pass

    def get_sharing_groups(self) -> list[MispSharingGroup]:
        pass

    def remove_blocked_events(self, event_ids: list[int]) -> list[int]:
        pass

    def get_attribute_with_correlations(self, value: str) -> list[MispEventAttribute]:
        pass

    def get_users_in_org(self, org_id: str) -> list[MispUser]:
        pass

    def get_users_of_posts_with_thread_id(self, thread_id: int) -> list[MispUser]:
        pass

    def get_values_with_correlation(self) -> list[str]:
        pass

    def get_over_correlating_values(self) -> list[tuple[str, int]]:
        pass

    def get_excluded_correlations(self) -> list[str]:
        pass

    def get_thread(self, thread_id: str) -> MispThread:
        pass

    def get_post(self, post_id: int) -> MispPost:
        pass

    def is_excluded_correlation(self, value: str) -> bool:
        pass

    def is_over_correlating_value(self, value: str) -> bool:
        pass

    def get_number_of_correlations(self, value: str) -> int:
        pass

    def add_correlation_value(self, value: str) -> int:
        # überprüfen ob value schon da
        pass

    def add_correlations(self, correlations: list[MispCorrelation]) -> bool:
        # überprüfen ob correlation schon da
        pass

    def add_over_correlating_value(self, value: str, count: int) -> bool:
        # überprüfen ob correlation schon da
        pass

    def delete_over_correlating_value(self, value: str) -> bool:
        pass

    def delete_correlations(self, value: str) -> bool:
        pass
