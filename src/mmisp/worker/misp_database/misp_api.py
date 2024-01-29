from typing import Mapping
from typing import TypeAlias
from uuid import UUID

from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import EventTagRelationship, AttributeTagRelationship
from mmisp.worker.misp_dataclasses.misp_tag import MispTag
from mmisp.worker.misp_dataclasses.misp_user import MispUser

JsonType: TypeAlias = list['JsonValue'] | Mapping[str, 'JsonValue']
JsonValue: TypeAlias = str | int | float | None | JsonType


class MispAPI:
    def is_server_reachable(self, server_id: int) -> bool:
        pass

    def get_server_settings(self, server_id: int) -> MispServer:
        # check the version of the server
        pass

    def get_server_version(self, server_id: int) -> MispServerVersion:
        pass

    def get_custom_cluster_from_server(self, conditions: JsonType, server_id: int) \
            -> list[MispGalaxyCluster]:
        pass

    def get_galaxy_cluster(self, cluster_id: int, server_id: int) -> MispGalaxyCluster:
        pass

    def get_event_views_from_server(self, ignore_filter_rules: bool, server_id: int) -> list[MispEvent]:
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

    def filter_event_ids_for_push(self, events: list[UUID], server_id: int) -> list[UUID]:
        pass

    def set_last_pulled_id(self, server_id: int) -> bool:
        pass

    def set_last_pushed_id(self, server_id: int) -> bool:
        pass

    def save_cluster(self, cluster: MispGalaxyCluster, server_id: int) -> bool:
        pass

    def save_event(self, event: MispEvent, server_id: int) -> bool:
        pass

    def save_proposal(self, event: MispEvent, server_id: int) -> bool:
        pass

    def save_sightings(self, sightings: list[MispSighting], server_id: int) -> int:
        pass

    def get_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        pass

    def get_event_attributes(self, event_id: int) -> list[MispEventAttribute]:
        pass

    def create_attribute(self, attribute: MispEventAttribute) -> bool:
        pass

    def create_tag(self, attribute: MispTag) -> id:
        pass

    def attach_attribute_tag(self, relationship: AttributeTagRelationship) -> bool:
        pass

    def attach_event_tag(self, relationship: EventTagRelationship) -> bool:
        pass

    def get_user(self, user_id: int) -> MispUser:
        pass

    def get_object(self, object_id: int) -> MispObject:
        pass

    def get_sharing_group(self, sharing_group_id: int) -> MispSharingGroup:
        pass

    def __modify_event_tag_relationship(self, relationship: EventTagRelationship) -> bool:
        pass

    def __modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship) -> bool:
        pass
