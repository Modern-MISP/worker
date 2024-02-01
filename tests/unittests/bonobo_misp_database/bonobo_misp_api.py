from pydantic_core.core_schema import JsonType

from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event_view import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import AttributeTagRelationship, EventTagRelationship, MispTag
from mmisp.worker.misp_dataclasses.misp_user import MispUser


class BonoboMispAPI:
    def get_server(self, server_id: int) -> MispServer:
        pass

    def get_server_version(self, server: MispServer) -> MispServerVersion:
        pass

    def get_custom_clusters_from_server(self, conditions: JsonType, server: MispServer) \
            -> list[MispGalaxyCluster]:
        pass

    def get_galaxy_cluster(self, cluster_id: int, server: MispServer) -> MispGalaxyCluster:
        pass

    def get_minimal_events_from_server(self, ignore_filter_rules: bool, server: MispServer) -> list[MispMinimalEvent]:
        pass

    def get_event(self, event_id: int, server: MispServer = None) -> MispEvent:
        pass

    def get_sightings_from_event(self, event_id: int, server: MispServer) -> list[MispSighting]:
        pass

    def get_proposals(self, user_id: int, server: MispServer) -> list[MispProposal]:
        pass

    def get_sharing_groups(self, server: MispServer = None) -> list[MispSharingGroup]:
        pass

    def filter_event_ids_for_push(self, event_ids: list[int], server: MispServer) -> list[int]:
        pass

    def save_cluster(self, cluster: MispGalaxyCluster, server: MispServer) -> bool:
        pass

    def save_event(self, event: MispEvent, server: MispServer) -> bool:
        pass

    def save_proposal(self, event: MispEvent, server: MispServer) -> bool:
        pass

    def save_sighting(self, sighting: MispSighting, server: MispServer) -> bool:
        pass

    def get_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        pass

    def get_event_attributes(self, event_id: int) -> list[MispEventAttribute]:
        pass

    def create_attribute(self, attribute: MispEventAttribute) -> bool:
        pass

    def create_tag(self, attribute: MispTag) -> int:
        pass

    def attach_attribute_tag(self, relationship: AttributeTagRelationship) -> bool:
        pass

    def attach_event_tag(self, relationship: EventTagRelationship) -> bool:
        pass

    def get_user(self, user_id: int) -> MispUser | None:
        match user_id:
            case 1:
                return MispUser(id=1, org_id=1, server_id=0,
                                email="admin@admin.test",
                                autoalert=False,
                                authkey="WLubSZRh4xfovca2NhdvBnQ5BG9TJpDmKqjAKXTf",
                                invited_by=0,
                                gpgkey=None,
                                certif_public="",
                                nids_sid=4000000,
                                termsaccepted=False,
                                newsread=0,
                                role_id=1,
                                change_pw=False,
                                contactalert=False,
                                disabled=False,
                                expiration=None,
                                current_login=1706814989,
                                last_login=1706812551,
                                last_api_access=1706826751,
                                force_logout=False,
                                date_created=None,
                                date_modified=1706826751,
                                last_pw_change=1699633563)
            case _:
                return None

    def get_object(self, object_id: int) -> MispObject:
        pass

    def get_sharing_group(self, sharing_group_id: int) -> MispSharingGroup:
        pass

    def modify_event_tag_relationship(self, relationship: EventTagRelationship) -> bool:
        pass

    def modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship) -> bool:
        pass
