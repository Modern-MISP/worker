from uuid import UUID

from mmisp.worker.misp_dataclasses.misp_correlation import MispCorrelation
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_post import MispPost
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import MispTag
from mmisp.worker.misp_dataclasses.misp_thread import MispThread


class MispSQL:

    def get_sharing_groups(self) -> list[MispSharingGroup]:
        pass

    def filter_blocked_events(self, events: list[MispEvent], use_event_blocklist: bool, use_org_blocklist: bool) \
            -> list[MispEvent]:
        pass

    def filter_blocked_clusters(self, clusters: list[MispGalaxyCluster]) -> list[MispGalaxyCluster]:
        # GalaxyClusterBlocklist
        pass

    def get_attributes_with_same_value(self, value: str) -> list[MispEventAttribute]:
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

    def get_number_of_correlations(self, value: str, only_correlation_table: bool) -> int:
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
        # correlation_values löschen
        # dann einträge aus default correlation löschen
        pass
