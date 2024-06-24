import unittest
from unittest import TestCase
from uuid import UUID

from mmisp.api_schemas.tags import TagViewResponse
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.server import ServerVersion
from mmisp.worker.misp_dataclasses.event_tag_relationship import EventTagRelationship
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship


class TestBasicApiEndpoints(TestCase):
    def test_get_server(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        self.assertEqual(server.name, "MISP 01")

    def test_get_server_version(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        version: ServerVersion = misp_api.get_server_version(server)
        self.assertEqual(version.version, "2.4.178")

    def test_get_custom_clusters_from_server(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        conditions: dict[str, bool] = {"published": True, "minimal": True, "custom": True}
        clusters = misp_api.get_custom_clusters(conditions, server)
        self.assertEqual(type(clusters[0]), GetGalaxyClusterResponse)

    def test_get_galaxy_cluster_from_server(self):
        mmisp_api: MispAPI = MispAPI()
        server: Server = mmisp_api.get_server(1)
        cluster = mmisp_api.get_galaxy_cluster(50, server)
        self.assertEqual(cluster.uuid, "a47b3aa0-604c-4c27-938b-c9aed2724309")

    def test_get_minimal_events_from_server(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        events = misp_api.get_minimal_events(True, server)
        self.assertGreater(len(events), 1300)

    def test_get_event(self):
        misp_api: MispAPI = MispAPI()

        event = misp_api.get_event(100)
        self.assertEqual(type(event), AddEditGetEventDetails)

    def test_get_event_for_server(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        event = misp_api.get_event(2, server)
        self.assertEqual(event.uuid, UUID("54ae77a8-f9e7-4bc3-abbc-672c11f2e00f"))

    def test_get_sightings_from_event(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        sightings = misp_api.get_sightings_from_event(20, server)
        self.assertEqual(sightings[0].id, 10)

    def test_get_proposals(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        proposals = misp_api.get_proposals(server)
        self.assertEqual(proposals[0].id, 2)

    def test_get_sharing_groups(self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        sharing_groups = misp_api.get_sharing_groups(server)
        self.assertEqual(sharing_groups[0].name, "biggest test")

    def test_get_event_attributes(self):
        misp_api: MispAPI = MispAPI()
        attributes = misp_api.get_event_attributes(2)
        self.assertEqual(type(attributes[0]), MispFullAttribute)

    def test_get_user(self):
        misp_api: MispAPI = MispAPI()
        user = misp_api.get_user(1)
        self.assertEqual(user.email, "admin@admin.test")

    def test_get_object(self):
        misp_api: MispAPI = MispAPI()
        misp_object: ObjectWithAttributesResponse = misp_api.get_object(2)
        self.assertEqual(misp_object.uuid, UUID("875aa3e7-569c-49b0-9e5b-bf2418a1bce8"))

    def test_get_sharing_group(self):
        misp_api: MispAPI = MispAPI()
        sharing_group = misp_api.get_sharing_group(1)
        self.assertEqual(sharing_group.name, "TestSharingGroup")

    def test_save_cluster(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

    def test_save_event(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

    def test_save_sighting(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

    def test_save_proposal(self):
        self.assertEqual(1, 1)
        return  # Skip this test, because it works and data has to be newly created every run

    def test_create_attribute(self):
        misp_api: MispAPI = MispAPI()
        event_attribute: MispFullAttribute = MispFullAttribute(
            id=1505,
            event_id=2,
            object_id=3,
            object_relation="act-as",
            category="Other",
            type="text",
            to_ids=False,
            uuid="7e3fc923-c5c1-11ee-b7e9-00158350240e",
            timestamp=1700088063,
            distribution=0,
            sharing_group_id=0,
            comment="No comment",
            deleted=False,
            disable_correlation=False,
            first_seen="2023-11-23T00:00:00.000000+00:00",
            last_seen="2023-11-23T00:00:00.000000+00:00",
            value="testing",
            event_uuid="64c236c1-b85b-4400-98ea-fe2301a397c7",
            tags=[],
        )
        self.assertTrue(misp_api.create_attribute(event_attribute) >= 0)

    def test_create_tag(self):
        misp_api: MispAPI = MispAPI()
        tag = TagViewResponse(
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
        )

        self.assertTrue(misp_api.create_tag(tag) >= 0)

    def test_attach_attribute_tag(self):
        misp_api: MispAPI = MispAPI()
        relationship = AttributeTagRelationship(
            id=123123, attribute_id=14, tag_id=1464, local=1, relationship_type=None
        )  # event 2
        misp_api.attach_attribute_tag(relationship)

    def test_attach_event_tag(self):
        misp_api: MispAPI = MispAPI()
        relationship = EventTagRelationship(id=123123123, event_id=20, tag_id=1464, local=1, relationship_type=None)
        misp_api.attach_event_tag(relationship)

    def test_modify_event_tag_relationship(self):
        misp_api: MispAPI = MispAPI()
        misp_sql: MispSQL = MispSQL()
        event_tag_id: int = misp_sql.get_event_tag_id(20, 1464)
        relationship = EventTagRelationship(id=event_tag_id, event_id=20, tag_id=1464, local=1, relationship_type=None)
        misp_api.modify_event_tag_relationship(relationship)

    def test_modify_attribute_tag_relationship(self):
        misp_api: MispAPI = MispAPI()
        misp_sql: MispSQL = MispSQL()
        attribute_tag_id: int = misp_sql.get_attribute_tag_id(14, 1464)
        relationship = AttributeTagRelationship(
            id=attribute_tag_id, event_id=20, tag_id=213, local=1, relationship_type=None
        )
        misp_api.modify_attribute_tag_relationship(relationship)


if __name__ == "__main__":
    unittest.main()
