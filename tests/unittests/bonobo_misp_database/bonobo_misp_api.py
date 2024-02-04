import datetime

from pydantic_core.core_schema import JsonType

from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event_report import MispEventReport
from mmisp.worker.misp_dataclasses.misp_event_view import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_role import MispRole
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

        tags: list[tuple[MispTag, EventTagRelationship]] = [
            (
                MispTag(
                    id=1,
                    name="tlp:white",
                    colour="#ffffff",
                    exportable=True,
                    org_id=12345,
                    user_id=1,
                    hide_tag=False,
                    numerical_value=12345,
                    is_galaxy=True,
                    is_custom_galaxy=True,
                    inherited=1,
                    attribute_count=None,
                    local_only=True,
                    count=None,
                    favourite=False),
                EventTagRelationship(id=1, event_id=1, tag_id=1, local=None,
                                     relationship=None)
            )]

        match event_id:
            case 1: return MispEvent(id=1,
                                     org_id=1,
                                     date="2023 - 11 - 16",
                                     info="sdfas",
                                     uuid="fb2fa4a266e548a39bdd5c5ce78e11e8",
                                     extends_uuid="fb2fa4a266e548a39bdd5c5ce78e11e8",
                                     published=False,
                                     analysis=0,
                                     attribute_count=6,
                                     orgc_id=1,
                                     timestamp=1706736785,
                                     distribution=1,
                                     sharing_group_id=0,
                                     proposal_email_lock=False,
                                     locked=False,
                                     threat_level_id=4,
                                     publish_timestamp=1700496633,
                                     sighting_timestamp=0,
                                     disable_correlation=False,
                                     protected=None,
                                     event_creator_email="",
                                     shadow_attributes=None,
                                     attributes=None,
                                     related_events=None,
                                     clusters=None,
                                     objects=None,
                                     reports=None,
                                     tags=tags,
                                     cryptographic_key=None,
                                     org=MispOrganisation(id=1,
                                                          name="ORGNAME",
                                                          uuid="5019f511811a4dab800c80c92bc16d3d"),
                                     orgc=MispOrganisation(id=1, name="ORGNAME",
                                                           uuid="5019f511811a4dab800c80c92bc16d3d"))

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
                                email="lerngruppeMisp@outlook.de",
                                auto_alert=False,
                                authkey="WLubSZRh4xfovca2NhdvBnQ5BG9TJpDmKqjAKXTf",
                                invited_by=0,
                                gpgkey=None,
                                certif_public="",
                                nids_sid=4000000,
                                terms_accepted=False,
                                newsread=0,
                                role=MispRole(id=3,
                                              created=datetime.datetime(1, 1, 1),
                                              modified=datetime.datetime(1, 1, 1),
                                              name="ORGNAME",
                                              perm_add=True,
                                              perm_modify=True,
                                              perm_modify_org=True,
                                              perm_publish=True,
                                              perm_delegate=True,
                                              perm_sync=True,
                                              perm_admin=True,
                                              perm_audit=True,
                                              perm_auth=True,
                                              perm_site_admin=True,
                                              perm_regexp_access=True,
                                              perm_tagger=True,
                                              perm_template=True,
                                              perm_sharing_group=True,
                                              perm_tag_editor=True,
                                              perm_sighting=True,
                                              perm_object_template=True,
                                              perm_publish_zmq=True,
                                              perm_publish_kafka=True,
                                              perm_decaying=True,
                                              perm_galaxy_editor=True,
                                              perm_view_feed_correlations=1,
                                              default_role=True,
                                              memory_limit="string",
                                              max_execution_time="string",
                                              restricted_to_site_admin=True,
                                              enforce_rate_limit=True,
                                              rate_limit_count=1,
                                              permission="3",
                                              perm_warninglist=1,
                                              permission_description="publish"),
                                change_pw=False,
                                contact_alert=False,
                                disabled=False,
                                expiration=None,
                                current_login=1706814989,
                                last_login=1706812551,
                                last_api_access=1706826751,
                                force_logout=False,
                                date_created=None,
                                date_modified=1706826751,
                                last_pw_change=1699633563,
                                password="passwort")
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
