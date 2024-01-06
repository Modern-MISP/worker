from typing import List

from kit.misp_database.misp_api import JsonType
from kit.misp_dataclasses import misp_galaxy_cluster
from kit.misp_dataclasses.mips_event import MispEvent
from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.misp_dataclasses.misp_tag import MispTag


class MispSQL:
    def fetch_galaxy_clusters(self, user_id: int, options: JsonType, full: bool = False,
                              include_full_cluster_relationship: bool = False) -> List[GalaxyCluster]:
        pass

    def fetch_event_ids(self, find_param: str) -> List[int]:
        pass

    def filter_event_ids_for_push(self, events: List[int]) -> List[int]:
        pass

    def fetch_event(self, user_id: int, param: str) -> MispEvent:
        pass

    def write_event_attribute(self, attribute: MispEventAttribute):
        pass

    def create_tag(self, tag: MispTag):
        pass

    def attach_event_tag(self, event_id: int, tag: MispTag):
        pass

    def attach_attribute_tag(self, attribute_id: int, tag: MispTag):
        pass
