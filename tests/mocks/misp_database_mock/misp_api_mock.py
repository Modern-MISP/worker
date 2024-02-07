import datetime
import uuid
from typing import Any
from unittest.mock import Mock

from pydantic_core.core_schema import JsonType

from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event_view import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_object_attribute import MispObjectAttribute
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_role import MispRole
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import AttributeTagRelationship, EventTagRelationship, MispTag
from mmisp.worker.misp_dataclasses.misp_user import MispUser


class MispAPIMock(Mock):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.__created_tag = None
        self.__created_attribute = None

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
            )
        ]

        match event_id:
            case 1:
                return MispEvent(id=1,
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
                                 distribution=4,
                                 sharing_group_id=1,
                                 proposal_email_lock=False,
                                 locked=False,
                                 threat_level_id=1,
                                 publish_timestamp=1700496633,
                                 sighting_timestamp=0,
                                 disable_correlation=False,
                                 protected=None,
                                 event_creator_email="",
                                 shadow_attributes=None,
                                 attributes=[self.get_event_attribute(1)],
                                 related_events=[self.get_event(2)],  # attention: recursive call
                                 clusters=None,
                                 objects=[self.get_object(1)],
                                 reports=None,
                                 tags=tags,
                                 cryptographic_key=None,
                                 org=MispOrganisation(id=1,
                                                      name="ORGNAME",
                                                      uuid="5019f511811a4dab800c80c92bc16d3d",
                                                      local=True),
                                 orgc=MispOrganisation(id=1, name="ORGNAME",
                                                       uuid="5019f511811a4dab800c80c92bc16d3d",
                                                       local=True))
            # attention: get_event(2) is called in get_event(1)
            case 2:
                return MispEvent(id=2, org_id=1, date="2023-11-16", info="sdfas",
                                 uuid="5019f511811a4dab800c80c92bc16d3d",
                                 extends_uuid="5019f511811a4dab800c80c92bc16d3d",
                                 published=False, analysis=0, attribute_count=6, orgc_id=1,
                                 timestamp=1706736785, distribution=4, sharing_group_id=0,
                                 proposal_email_lock=False, locked=False, threat_level_id=1,
                                 publish_timestamp=1700496633, sighting_timestamp=0,
                                 disable_correlation=False, protected=None,
                                 event_creator_email="", shadow_attributes=None,
                                 attributes=[self.get_event_attribute(1)],
                                 related_events=None, clusters=None, objects=[self.get_object(1)],
                                 reports=None, tags=tags, cryptographic_key=None,
                                 org=MispOrganisation(id=1, name="ORGNAME",
                                                      uuid="5019f511811a4dab800c80c92bc16d3d",
                                                      local=True),
                                 orgc=MispOrganisation(id=1, name="ORGNAME",
                                                       uuid="5019f511811a4dab800c80c92bc16d3d",
                                                       local=True))

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

        attribute: MispEventAttribute = MispEventAttribute(
            id=1, event_id=20, object_id=3, object_relation='act-as',
            category='Other', type='text', to_ids=False,
            uuid='40817bc9-123e-43da-a5e1-aa15a9a4ea6d',
            timestamp=1700088063, distribution=0, sharing_group_id=0,
            comment='No comment', deleted=False, disable_correlation=False,
            first_seen='2023-11-23T00:00:00.000000+00:00', last_seen='2023-11-23T00:00:00.000000+00:00',
            value="Very important information.", event_uuid="64c236c1-b85b-4400-98ea-fe2301a397c7",
            tags=
            [(
                MispTag(
                    id=2, name="tlp:white", colour="#ffffff", exportable=True, org_id=12345, user_id=1,
                    hide_tag=False, numerical_value=12345, is_galaxy=True, is_custom_galaxy=True,
                    local_only=True, inherited=1, attribute_count=3, count=3, favourite=False),
                AttributeTagRelationship(
                    id=10, attribute_id=1, tag_id=2, local=0, relationship_type=None)
            )]
        )

        match attribute_id:
            case 1:
                return attribute
            case 12:
                attribute.type = "Any"
                return attribute

    def get_event_attributes(self, event_id: int) -> list[MispEventAttribute]:
        match event_id:
            case 1:
                return [
                    MispEventAttribute(
                        id=1, event_id=1, object_id=3, object_relation='act-as',
                        category='Other', type='text', to_ids=False,
                        uuid='40817bc9-123e-43da-a5e1-aa15a9a4ea6d',
                        timestamp=1700088063, distribution=0, sharing_group_id=0,
                        comment='No comment', deleted=False, disable_correlation=False,
                        first_seen='2023-11-23T00:00:00.000000+00:00', last_seen='2023-11-23T00:00:00.000000+00:00',
                        value="Very important information.", event_uuid="64c236c1-b85b-4400-98ea-fe2301a397c7",
                        data=None,
                        tags=
                        [(
                            MispTag(
                                id=2, name="tlp:white", colour="#ffffff", exportable=True, org_id=12345, user_id=1,
                                hide_tag=False, numerical_value=12345, is_galaxy=True, is_custom_galaxy=True,
                                local_only=True, inherited=1, attribute_count=3, count=3, favourite=False),
                            AttributeTagRelationship(
                                id=10, attribute_id=1, tag_id=2, local=0, relationship_type=None)
                        )]),
                    MispEventAttribute(
                        id=2, event_id=1, object_id=2, object_relation='act-as',
                        category='Other', type='text', to_ids=False,
                        uuid='f2ccde59-bbc5-4c36-a7b8-6fc69dbb94a4',
                        timestamp=1700575335, distribution=0, sharing_group_id=0,
                        comment='No comment', deleted=False, disable_correlation=False,
                        first_seen=None, last_seen=None,
                        value="Example test.", event_uuid="64c236c1-b85b-4400-98ea-fe2301a397c7",
                        data=None,
                        tags=
                        [(
                            MispTag(
                                id=3, name="tlp:black", colour="#000000", exportable=True, org_id=12346, user_id=2,
                                hide_tag=False, numerical_value=12346, is_galaxy=True, is_custom_galaxy=True,
                                local_only=True, inherited=1, attribute_count=4, count=4, favourite=False),
                            AttributeTagRelationship(
                                id=11, attribute_id=1, tag_id=3, local=0, relationship_type=None)
                        )])
                ]

    def create_attribute(self, attribute: MispEventAttribute) -> bool:
        self.__created_attribute: MispEventAttribute = attribute
        return True

    def get_created_attribute(self) -> MispEventAttribute:
        return self.__created_attribute

    def create_tag(self, tag: MispTag) -> int:
        self.__created_tag: MispTag = tag
        return 1

    def get_created_tag(self) -> MispTag:
        return self.__created_tag

    def attach_attribute_tag(self, relationship: AttributeTagRelationship) -> bool:
        pass

    def attach_event_tag(self, relationship: EventTagRelationship) -> bool:
        pass

    def get_user(self, user_id: int) -> MispUser | None:
        match user_id:
            case 1:
                return MispUser(id=1, org_id=1, server_id=0,
                                email="lerngruppeMisp@outlook.de", # TODO Email löschen vor der finalen Abgabe
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
        match object_id:
            case 1: return MispObject(id=1, name="TestObject", meta_category="TestMetaCategory",
                                      description="TestDescription",
                                      template_uuid="123e4567-e89b-12d3-a456-426614174000", template_version=1,
                                      event_id=1,
                                      uuid="123e4567-e89b-12d3-a456-426614174000", timestamp=1700988063,
                                      distribution=1, sharing_group_id=1, comment="TestComment", deleted=False,
                                      first_seen=datetime.datetime(1, 1, 1),
                                      last_seen=datetime.datetime(1, 1, 1),
                                      attributes=[
                                          MispObjectAttribute(id=1, event_id=1, object_id=1,
                                                              object_relation="TestObjectRelation",
                                                              category="TestCategory", type="TestType", to_ids=True,
                                                              uuid="123e4567-e89b-12d3-a456-426614174000",
                                                              timestamp=datetime.datetime(1, 1, 1),
                                                              distribution=1, sharing_group_id=1, comment="TestComment",
                                                              deleted=False, disable_correlation=False,
                                                              first_seen=datetime.datetime(1, 1, 1),
                                                              last_seen=datetime.datetime(1, 1, 1),
                                                              value="TestValue", data=None,
                                                              tags=[(MispTag(id=1, name="TestTag", colour="#ffffff",
                                                                             exportable=True, org_id=1, user_id=1,
                                                                             hide_tag=False, numerical_value=1,
                                                                             is_galaxy=True, is_custom_galaxy=True,
                                                                             local_only=True, inherited=1,
                                                                             attribute_count=1, count=1,
                                                                             favourite=True),
                                                                     AttributeTagRelationship(id=1, attribute_id=1,
                                                                                              tag_id=1, local=1,
                                                                                              relationship_type=
                                                                                              "TestRelationshipType")
                                                                     )
                                                                    ]
                                                              )
                                      ]
                                      )
        match object_id:
            case 66: return MispObject(id=66, name="test", meta_category="test", description="test",
                                       template_uuid=uuid.uuid4(), template_version=1, event_id=66, uuid=uuid.uuid4(),
                                       timestamp=datetime.datetime(1, 1, 1), distribution=1, sharing_group_id=1,
                                       comment="test", deleted=False, first_seen=datetime.datetime(1, 1, 1),
                                       last_seen=datetime.datetime(1, 1, 1), attributes=[])

    def get_sharing_group(self, sharing_group_id: int) -> MispSharingGroup | None:
        match sharing_group_id:
            case 1:
                return MispSharingGroup(id=1,
                                        name="TestSharingGroup",
                                        releasability="keine Ahnung was ich hier reinschreibe",
                                        description="babla",
                                        uuid="336a9e10-2a77-406b-a63c-04f66ba948fb",
                                        organisation_uuid="5019f511-811a-4dab-800c-80c92bc16d3d",
                                        org_id=1,
                                        sync_user_id=0,
                                        active=True,
                                        created="2024-01-30 20=00=13",
                                        modified="2024-01-30 20=10=42",
                                        local=True,
                                        roaming=False,
                                        organisation=MispOrganisation(id=1,
                                                                      name="ZWEI",
                                                                      date_created=datetime.datetime(1, 1, 1),
                                                                      date_modified=datetime.datetime(1, 1, 1),
                                                                      description="Auf misp-02 Organisation",
                                                                      type="ADMIN",
                                                                      nationality="",
                                                                      sector="",
                                                                      created_by=0,
                                                                      uuid="387a5a4f-3b45-4f7a-9681-46926326516b",
                                                                      contacts="",
                                                                      local=True,
                                                                      restricted_to_domain=[],
                                                                      landingpage=None),
                                        sharing_group_orgs=[MispSharingGroupOrg(id=1, sharing_group_id=1,
                                                                                org_id=1,
                                                                                extend=True,
                                                                                org_name="ZWEI",
                                                                                org_uuid="387a5a4f3b454f7a968146926"
                                                                                         "326516b",
                                                                                )],
                                        sharing_group_servers=[MispSharingGroupServer(id=1,
                                                                                      sharing_group_id=1,
                                                                                      server_id=0,
                                                                                      all_orgs=True,
                                                                                      server_name="Local instance")])

            case _:
                return None

    def modify_event_tag_relationship(self, relationship: EventTagRelationship) -> bool:
        # TODO: How to test?
        pass

    def modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship) -> bool:
        # TODO: How to test?
        pass
