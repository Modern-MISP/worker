from typing import Dict
from typing import TypeAlias
from typing import List
from typing import Mapping

from src.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from src.misp_dataclasses.misp_event import MispEvent
from src.misp_dataclasses.misp_attribute import MispEventAttribute
from src.misp_dataclasses.misp_server_version import MispServerVersion
from src.misp_dataclasses.misp_tag import MispTag
from src.misp_dataclasses.misp_proposal import MispProposal
from src.misp_dataclasses.misp_sighting import MispSighting
from src.misp_dataclasses.misp_server import MispServer
from src.misp_dataclasses.misp_tag import EventTagRelationship, AttributeTagRelationship

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

    def get_custom_cluster_ids_from_server(self, server_id, conditions: JsonType) -> List[int]:
        pass

    def get_galaxy_cluster(self, server_id: int, cluster_id: int, user_id: int) -> MispGalaxyCluster:
        pass

    def save_cluster(self, server_id, cluster: MispGalaxyCluster) -> bool:
        pass

    def get_event_ids_from_server(self, server_id: int, ignore_filter_rules: bool) -> List[int]:
        pass

    def get_event(self, event_id: int, server_id: int) -> MispEvent:
        pass

    def save_event(self, server_id: int, event: MispEvent) -> bool:
        pass

    def get_sightings(self, user_id: int, server_id: int) -> List[MispSighting]:
        pass

    def get_proposals(self, user_id: int, server_id: int) -> List[MispProposal]:
        pass

    def save_sightings(self, server_id: int, sighting: MispSighting) -> bool:
        pass

    def save_proposal(self, server_id: int, proposal: MispProposal) -> bool:
        pass

    def get_sharing_groups_ids(self, server_id: int) -> List[int]:
        pass

    def get_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        pass

    def get_event_attributes(self, event_id: int) -> List[MispEventAttribute]:
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
