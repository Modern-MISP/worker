from typing import Dict
from typing import TypeAlias
from typing import List
from typing import Mapping

JsonType: TypeAlias = List['JsonValue'] | Mapping[str, 'JsonValue']
JsonValue: TypeAlias = str | int | float | None | JsonType

# should save for every server a last-pushed-id
class MispAPI:
    def is_server_reachable(self, server_id: int) -> bool:
        pass

    def get_server_settings(self, server_id: int) -> Dict[str, str]:
        pass

    def check_version_compatibility(self, server_id: int, user_id: int):
        pass

    def fetch_custom_cluster_ids_from_server(self, server_id, conditions: JsonType) -> List[int]:
        pass

    def fetch_galaxy_cluster(self, server_id: int, cluster_id: int, user_id: int) -> JsonType:
        pass

    def save_cluster(self, server_id, cluster: JsonType) -> bool:
        pass

    def get_event_ids_from_server(self, ignore_filter_rules: bool):
        pass

    def fetch_event(self, event_id: int) -> JsonType:
        pass

    def save_event(self, event: JsonType) -> bool:
        pass

    def fetch_sightings(self, user_id: int, server_id: int) -> List[JsonType]:
        pass

    def fetch_proposals(self, user_id: int, server_id: int) -> List[JsonType]:
        pass

    def save_proposal(self, proposal: JsonType) -> bool:
        pass

    def save_sightings(self, sighting: JsonType) -> bool:
        pass

    def push_cluster(self, user_id: int, cluster: JsonType) -> bool:
        pass

    def get_sharing_groups_ids(self, server_id: int) -> List[int]:
        pass

    def upload_cluster_to_server(self, user_id, cluster) -> bool:
        pass

    def upload_event_to_server(self, event) -> bool:
        pass