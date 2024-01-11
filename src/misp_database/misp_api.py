from typing import TypeAlias
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
from src.misp_dataclasses.misp_user import MispUser

JsonType: TypeAlias = list['JsonValue'] | Mapping[str, 'JsonValue']
JsonValue: TypeAlias = str | int | float | None | JsonType


class MispAPI:
    def is_server_reachable(self, server_id: int) -> bool:

        pass

    def get_server_settings(self, server_id: int) -> MispServer:
        pass

    def get_server_version(self, server_id: int) -> MispServerVersion:
        pass

    def get_custom_cluster_ids_from_server(self, conditions: JsonType, server_id: int) -> list[int]:
        pass

    def get_galaxy_cluster(self, cluster_id: int, server_id: int) -> MispGalaxyCluster:
        pass

    def get_event_ids_from_server(self, ignore_filter_rules: bool, server_id: int) -> list[int]:
        pass

    def get_event_from_server(self, event_id: int, server_id: int) -> MispEvent:
        pass

    def get_event(self, event_id: int) -> MispEvent:
        pass

    def get_sightings(self, user_id: int, server_id: int) -> list[MispSighting]:
        pass

    def get_proposals(self, user_id: int, server_id: int) -> list[MispProposal]:
        pass

    def get_sharing_groups_ids(self, server_id: int) -> list[int]:
        pass

    def filter_event_ids_for_push(self, events: list[int], server_id: int) -> list[int]:
        pass

    def set_last_pulled_id(self, server_id: int) -> bool:
        pass

    def set_last_pushed_id(self, server_id: int) -> bool:
        pass

    def save_cluster(self, cluster: MispGalaxyCluster, server_id: int) -> bool:
        pass

    def save_event(self, event: MispEvent, server_id: int) -> bool:
        pass

    def get_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        pass

    def get_event_attributes(self, event_id: int) -> list[MispEventAttribute]:
        pass

    def create_attribute(self, attribute: MispEventAttribute) -> bool:
        pass

    def create_tag(self, attribute: MispTag) -> bool:
        pass

    def attach_attribute_tag(self, relationship: AttributeTagRelationship) -> bool:
        pass

    def attach_event_tag(self, relationship: EventTagRelationship) -> bool:
        pass

    def get_user(self, user_id: int) -> MispUser:
        pass

    def __modify_event_tag_relationship(self, relationship: EventTagRelationship) -> bool:
        pass

    def __modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship) -> bool:
        pass
