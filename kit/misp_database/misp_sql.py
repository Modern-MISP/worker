from typing import List

from kit.misp_database.misp_api import JsonType


class MispSQL:
    def fetch_galaxy_clusters(self, user_id: int, options: JsonType, full: bool = False,
                              include_full_cluster_relationship: bool = False) -> List[JsonType]:
        pass

    def fetch_event_ids(self, find_param: str) -> List[int]:
        pass

    def filter_event_ids_for_push(self, events: List[int]) -> List[int]:
        pass

    def fetch_event(self, user_id: int, param: str) -> JsonType:
        pass