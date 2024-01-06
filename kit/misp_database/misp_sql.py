from typing import List

from kit.misp_database.misp_api import JsonType
from kit.misp_dataclasses import galaxy_cluster
from kit.misp_dataclasses.misp_correlation import Correlation
from kit.misp_dataclasses.misp_event import Event
from kit.misp_dataclasses.misp_attribute import EventAttribute
from kit.misp_dataclasses.misp_tag import Tag


class MispSQL:
    def fetch_galaxy_clusters(self, user_id: int, options: JsonType, full: bool = False,
                              include_full_cluster_relationship: bool = False) -> List[GalaxyCluster]:
        pass

    def fetch_event_ids(self, find_param: str) -> List[int]:
        pass

    def filter_event_ids_for_push(self, events: List[int]) -> List[int]:
        pass

    def fetch_event(self, user_id: int, param: str) -> Event:
        pass

    def write_event_attribute(self, attribute: EventAttribute):
        pass

    def create_tag(self, tag: Tag):
        pass

    def attach_event_tag(self, event_id: int, tag: Tag):
        pass

    def attach_attribute_tag(self, attribute_id: int, tag: Tag):
        pass

    def is_excluded_correlation(self, value: str) -> bool:
        pass

    def is_over_correlating_value(self, value: str) -> bool:
        pass

    def fetch_attribute_correlations(self, value: str) -> List[EventAttribute]:
        pass

    def add_correlation_value(self, value: str) -> int:
        # überprüfen ob value schon da
        pass

    def add_correlations(self, correlations: List[Correlation]) -> bool:
        # überprüfen ob correlation schon da
        pass

    def fetch_correlation_values(self) -> List[str]:
        pass

    def count_value_correlations(self, value: str) -> int:
        pass

    def fetch_over_correlating_values(self) -> List[str]:
        pass

    def add_over_correlating_value(self, value: str, count: int) -> bool:
        # überprüfen ob correlation schon da
        pass

    def delete_over_correlating_value(self, value: str) -> bool:
        pass

    def delete_correlations(self, value: str) -> bool:
        pass

    def get_users_in_org(self, org_id: str): #TODO list[user] als rückgabetyp hinzufügen
        pass

    def get_thread(self, thread_id: str): #TODO Thread als rückgabetyp hinzufügen
        pass

    def get_Post(self, post_id: str): #TODO post als rückgabetyp hinzufügen
        pass



