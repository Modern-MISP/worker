from typing import Dict
from typing import TypeAlias
from typing import List
from typing import Mapping

from kit.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from kit.misp_dataclasses.misp_event import MispEvent
from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.misp_dataclasses.misp_server_version import MispServerVersion
from kit.misp_dataclasses.misp_tag import MispTag
from kit.misp_dataclasses.misp_proposal import MispProposal
from kit.misp_dataclasses.misp_sighting import MispSighting
from kit.misp_dataclasses.misp_server import MispServer
from kit.misp_dataclasses.misp_tag import EventTagRelationship, AttributeTagRelationship

JsonType: TypeAlias = List['JsonValue'] | Mapping[str, 'JsonValue']
JsonValue: TypeAlias = str | int | float | None | JsonType


class MispAPI:
    # should save for every server a last-pushed-id

    def is_server_reachable(self, server_id: int) -> bool:

        pass

    def get_server_settings(self, server_id: int) -> MispServer:
        pass

    def set_last_pulled_id(self, server_id: int) -> bool:
        pass

    def set_last_pushed_id(self, server_id: int) -> bool:
        pass

    def get_server_version(self, server_id: int) -> MispServerVersion:
        pass

    def fetch_custom_cluster_ids_from_server(self, server_id, conditions: JsonType) -> List[int]:
        pass

    def fetch_galaxy_cluster(self, server_id: int, cluster_id: int, user_id: int) -> MispGalaxyCluster:
        pass

    def save_cluster(self, server_id, cluster: JsonType) -> bool:
        pass

    def get_event_ids_from_server(self, ignore_filter_rules: bool) -> List[int]:
        pass

    def fetch_event(self, event_id: int) -> MispEvent:
        pass

    def save_event(self, event: JsonType) -> bool:
        pass

    def fetch_sightings(self, user_id: int, server_id: int) -> List[MispSighting]:
        pass

    def fetch_proposals(self, user_id: int, server_id: int) -> List[MispProposal]:
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

    def fetch_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        pass

    def fetch_event_attributes(self, event_id: int) -> List[MispEventAttribute]:
        pass

    def create_attribute(self, attribute: MispEventAttribute) -> bool:
        pass

    def create_tag(self, attribute: MispTag) -> bool:
        pass

    def attach_attribute_tag(self, relationship: AttributeTagRelationship) -> bool:
        pass

    def attach_event_tag(self, relationship: EventTagRelationship) -> bool:
        pass

    def __modify_event_tag_relationship(self, relationship: EventTagRelationship) -> bool:
        pass

    def __modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship) -> bool:
        pass
