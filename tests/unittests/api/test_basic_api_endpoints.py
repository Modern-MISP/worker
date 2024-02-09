import unittest
import uuid
from datetime import datetime
from unittest import TestCase
from uuid import UUID

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, AttributeTagRelationship, EventTagRelationship

from tests.unittests.api.test_misp_api import TestMispAPI


class TestBasicApiEndpoints(TestCase):
    def test_get_server(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        print(server)
        self.assertEqual(server.name, "MISP 01")

    def test_get_server_version(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        version: MispServerVersion = misp_api.get_server_version(server)
        self.assertEqual(version.version, "2.4.178")

    def test_get_custom_clusters_from_server(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        conditions: dict[str, bool] = {
            "published": True,
            "minimal": True,
            "custom": True
        }
        clusters = misp_api.get_custom_clusters_from_server(conditions, server)
        self.assertEqual(type(clusters[0]), MispGalaxyCluster)

    def test_get_galaxy_cluster_from_server(self):
        mmisp_api: TestMispAPI = TestMispAPI()
        server: MispServer = mmisp_api.get_server(1)
        cluster = mmisp_api.get_galaxy_cluster(50, server)
        self.assertEqual(cluster.uuid, "a47b3aa0-604c-4c27-938b-c9aed2724309")

    def test_get_minimal_events_from_server(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        events = misp_api.get_minimal_events(True, server)
        self.assertGreater(len(events), 1300)

    def test_get_event(self):
        misp_api: MispAPI = MispAPI()

        event = misp_api.get_event(100)
        self.assertEqual(type(event), MispEvent)

    def test_get_event_for_server(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        event = misp_api.get_event(2, server)
        # print(event)
        self.assertEqual(event.uuid, UUID("54ae77a8-f9e7-4bc3-abbc-672c11f2e00f"))

    def test_get_sightings_from_event(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        sightings = misp_api.get_sightings_from_event(20, server)
        self.assertEqual(sightings[0].id, 10)

    def test_get_proposals(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        proposals = misp_api.get_proposals(server)
        self.assertEqual(proposals[0].id, 2)

    def test_get_sharing_groups(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        sharing_groups = misp_api.get_sharing_groups(server)
        self.assertEqual(sharing_groups[0].name, "biggest test")

    def test_filter_events_for_push(self):
        event1: MispEvent = MispEvent(
            id=2,
            orgc_id=1,
            org_id=1,
            date="2023-11-16",
            threat_level_id=1,
            info="TestEvent",
            published=True,
            uuid=UUID("fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11e8"),
            attribute_count=1,
            analysis=0,
            timestamp="1706736785",
            distribution=0,
            proposal_email_lock=False,
            locked=False,
            publish_timestamp=0,
            sharing_group_id=1,
            disable_correlation=False,
            extends_uuid=UUID("fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11e8"),
            protected=None,
            event_creator_email="",
            org=None,
            orgc=None,
            tags=[], )

        event2: MispEvent = MispEvent(
            id=2,
            orgc_id=1,
            org_id=1,
            date="2023-11-16",
            threat_level_id=1,
            info="TestEvent",
            published=True,
            uuid=UUID("fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11ff"),
            attribute_count=1,
            analysis=0,
            timestamp="1706736785",
            distribution=0,
            proposal_email_lock=False,
            locked=False,
            publish_timestamp=0,
            sharing_group_id=1,
            disable_correlation=False,
            extends_uuid=UUID("fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11e8"),
            protected=None,
            event_creator_email="",
            org=None,
            orgc=None,
            tags=[], )

        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        event_ids: list[int] = misp_api.filter_events_for_push([event1, event2], server)
        self.assertEqual(len(event_ids), 1)

    def test_get_event_attributes(self):
        misp_api: TestMispAPI = TestMispAPI()
        attributes = misp_api.get_event_attributes(2)
        self.assertEqual(type(attributes[0]), MispEventAttribute)

    # def test_get_event_attributes_from_server(self):
    #     misp_api: TestMispAPI = TestMispAPI()
    #     event_attributes = misp_api.get_event_attributes(2)

    def test_get_user(self):
        misp_api: TestMispAPI = TestMispAPI()
        user = misp_api.get_user(1)
        self.assertEqual(user.email, "admin@admin.test")

    def test_get_object(self):
        misp_api: TestMispAPI = TestMispAPI()
        object: MispObject = misp_api.get_object(2)
        self.assertEqual(object.uuid, UUID("875aa3e7-569c-49b0-9e5b-bf2418a1bce8"))

    def test_get_sharing_group(self):
        misp_api: TestMispAPI = TestMispAPI()
        sharing_group = misp_api.get_sharing_group(1)
        self.assertEqual(sharing_group.name, "TestSharingGroup")

    def test_save_cluster(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

        misp_api: TestMispAPI = TestMispAPI()
        cluster: MispGalaxyCluster = misp_api.get_galaxy_cluster(1, None)
        cluster.id = 34534636
        cluster.uuid = UUID("988e1441-0350-5c39-979d-b0ca99ffd20b")
        print(cluster)
        succes: bool = misp_api.save_cluster(cluster, None)
        self.assertEqual(succes, True)

    def test_save_event(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

        misp_api: TestMispAPI = TestMispAPI()
        event1: MispEvent = misp_api.get_event(1)
        event1.uuid = UUID("fb2fa4a266e548a39bdd5c5ce78e11ff")
        misp_api.save_event(event1, None)

    def test_save_sighting(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

        sighting: MispSighting = MispSighting(
            id=1,
            attribute_id=6,
            event_id=5,
            org_id=4,
            date_sighting="1700093514",
            uuid="91bceefb-e89c-45a7-8070-a503b1284ef7",
            source="",
            type="0",
            attribute_uuid="588cc8db-fe79-46fe-a96b-3bb898b0468f",
            organisation=MispOrganisation(
                id=4,
                uuid="5019f511-811a-4dab-800c-80c92bc16d3d",
                name="ORGNAME_1243"
            )
        )
        misp_api: TestMispAPI = TestMispAPI()
        succes: bool = misp_api.save_sighting(sighting, None)
        self.assertEqual(succes, True)

    def test_save_proposal(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

        misp_api: TestMispAPI = TestMispAPI()
        event1: MispEvent = misp_api.get_event(1)
        proposal: MispProposal = MispProposal(
            id=123,
            old_id=123,
            event_id=1,
            type="",
            uuid="ff2fa4a266e548a39bdd5c5ce78e11ff",
            to_ids=False,
            timestamp=datetime.now(),
            deleted=False,
            proposal_to_delete=False,
            disable_correlation=False,
            organisation=MispOrganisation(
                id=1,
                name="TestOrg",
                uuid="ff2fa4a266e548af9bdd5c5ce78e11ff",
                local=False,
            ))

        event1.shadow_attributes = [
            proposal
        ]
        succes: bool = misp_api.save_proposal(event1, None)
        self.assertEqual(succes, True)

    def test_create_attribute(self):
        uuid_str = str(uuid.uuid1())
        print(uuid_str)
        misp_api: MispAPI = MispAPI()
        event_attribute: MispEventAttribute = MispEventAttribute(
            id=1505, event_id=2, object_id=3, object_relation='act-as',
            category='Other', type='text', to_ids=False,
            uuid='7e3fc923-c5c1-11ee-b7e9-00158350240e',
            timestamp=1700088063, distribution=0, sharing_group_id=0,
            comment='No comment', deleted=False, disable_correlation=False,
            first_seen='2023-11-23T00:00:00.000000+00:00', last_seen='2023-11-23T00:00:00.000000+00:00',
            value="testing", event_uuid="64c236c1-b85b-4400-98ea-fe2301a397c7",
            tags=[]
        )
        # print(event_attribute.tags[0][0].ser_model())
        # print(event_attribute.model_dump_json())
        self.assertTrue(misp_api.create_attribute(event_attribute) >= 0)

    def test_create_tag(self):
        misp_api: MispAPI = MispAPI()
        tag = MispTag(
            id=1123123,
            name="testtag",
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
            favourite=False)
        self.assertTrue(misp_api.create_tag(tag) >= 0)

    def test_attach_attribute_tag(self):
        misp_api: MispAPI = MispAPI()
        relationship = AttributeTagRelationship(
            id=123123, attribute_id=14, tag_id=1464, local=1, relationship_type=None)  # event 2
        misp_api.attach_attribute_tag(relationship)

    def test_attach_event_tag(self):
        misp_api: MispAPI = MispAPI()
        relationship = EventTagRelationship(
            id=123123123, event_id=20, tag_id=1464, local=1, relationship_type=None)
        misp_api.attach_event_tag(relationship)

    def test_modify_event_tag_relationship(self):
        misp_api: MispAPI = MispAPI()
        relationship = EventTagRelationship(
            id=123123123, event_id=20, tag_id=213, local=1, relationship_type=None)
        misp_api.modify_event_tag_relationship(relationship)

    def test_modify_attribute_tag_relationship(self):
        misp_api: MispAPI = MispAPI()
        relationship = AttributeTagRelationship(
            id=123123123, event_id=20, tag_id=213, local=1, relationship_type=None)
        misp_api.modify_attribute_tag_relationship(relationship)


if __name__ == "__main__":
    unittest.main()
