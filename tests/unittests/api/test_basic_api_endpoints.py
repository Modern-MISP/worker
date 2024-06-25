import unittest
from typing import Self
from unittest import TestCase
from uuid import UUID

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.server import Server, ServerVersion
from mmisp.api_schemas.tags import TagViewResponse
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL


class TestBasicApiEndpoints(TestCase):
    def test_get_server(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        self.assertEqual(server.name, "MISP 01")

    def test_get_server_version(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        version: ServerVersion = misp_api.get_server_version(server)
        self.assertEqual(version.version, "2.4.178")

    def test_get_custom_clusters_from_server(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        conditions: dict[str, bool] = {"published": True, "minimal": True, "custom": True}
        clusters = misp_api.get_custom_clusters(conditions, server)
        self.assertEqual(type(clusters[0]), GetGalaxyClusterResponse)

    def test_get_galaxy_cluster_from_server(self: Self):
        mmisp_api: MispAPI = MispAPI()
        server: Server = mmisp_api.get_server(1)
        cluster = mmisp_api.get_galaxy_cluster(50, server)
        self.assertEqual(cluster.uuid, "a47b3aa0-604c-4c27-938b-c9aed2724309")

    def test_get_minimal_events_from_server(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        events = misp_api.get_minimal_events(True, server)
        self.assertGreater(len(events), 1300)

    def test_get_event(self: Self):
        misp_api: MispAPI = MispAPI()

        event = misp_api.get_event(100)
        self.assertEqual(type(event), AddEditGetEventDetails)

    def test_get_event_for_server(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        event = misp_api.get_event(2, server)
        self.assertEqual(event.uuid, UUID("54ae77a8-f9e7-4bc3-abbc-672c11f2e00f"))

    def test_get_sightings_from_event(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        sightings = misp_api.get_sightings_from_event(20, server)
        self.assertEqual(sightings[0].id, 10)

    def test_get_proposals(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)
        proposals = misp_api.get_proposals(server)
        self.assertEqual(proposals[0].id, 2)

    def test_get_sharing_groups(self: Self):
        misp_api: MispAPI = MispAPI()
        server: Server = misp_api.get_server(1)

        sharing_groups = misp_api.get_sharing_groups(server)
        self.assertEqual(sharing_groups[0].SharingGroup.name, "biggest test")

    def test_get_event_attributes(self: Self):
        misp_api: MispAPI = MispAPI()
        attributes = misp_api.get_event_attributes(2)
        self.assertEqual(type(attributes[0]), AttributeWithTagRelationship)

    def test_get_user(self: Self):
        misp_api: MispAPI = MispAPI()
        user = misp_api.get_user(1)
        self.assertEqual(user.email, "admin@admin.test")

    def test_get_object(self: Self):
        misp_api: MispAPI = MispAPI()
        misp_object: ObjectWithAttributesResponse = misp_api.get_object(2)
        self.assertEqual(misp_object.uuid, UUID("875aa3e7-569c-49b0-9e5b-bf2418a1bce8"))

    def test_get_sharing_group(self: Self):
        misp_api: MispAPI = MispAPI()
        sharing_group = misp_api.get_sharing_group(1)
        self.assertEqual(sharing_group.SharingGroup.name, "TestSharingGroup")

    def test_create_attribute(self: Self):
        misp_api: MispAPI = MispAPI()
        event_attribute: AttributeWithTagRelationship = AttributeWithTagRelationship(
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
        # TODO Amadeus
        self.assertGreaterEqual(misp_api.create_attribute(event_attribute), 0)

    def test_create_tag(self: Self):
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
        # TODO Amadeus
        self.assertGreaterEqual(misp_api.create_tag(tag), 0)

    def test_attach_attribute_tag(self: Self):
        misp_api: MispAPI = MispAPI()
        misp_api.attach_attribute_tag(attribute_id=14, tag_id=1464, local=True)

    def test_attach_event_tag(self: Self):
        misp_api: MispAPI = MispAPI()
        misp_api.attach_event_tag(event_id=20, tag_id=1464, local=True)

    def test_modify_event_tag_relationship(self: Self):
        misp_api: MispAPI = MispAPI()
        misp_sql: MispSQL = MispSQL()
        event_tag_id: int = misp_sql.get_event_tag_id(20, 1464)
        misp_api.modify_event_tag_relationship(event_tag_id=event_tag_id, relationship_type="")

    def test_modify_attribute_tag_relationship(self: Self):
        misp_api: MispAPI = MispAPI()
        misp_sql: MispSQL = MispSQL()
        attribute_tag_id: int = misp_sql.get_attribute_tag_id(14, 1464)
        misp_api.modify_attribute_tag_relationship(attribute_tag_id=attribute_tag_id, relationship_type="")


if __name__ == "__main__":
    unittest.main()
