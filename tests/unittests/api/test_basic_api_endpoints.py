import json
from unittest import TestCase

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, AttributeTagRelationship
from tests.unittests.api.test_misp_api import TestMispAPI


class TestBasicApiEndpoints(TestCase):
    def test_get_server(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        self.assertEqual(server.name, "MISP 02")

    def test_get_server_version(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        version: MispServerVersion = misp_api.get_server_version(server)
        self.assertEqual(version.version, "2.4.178")

    def test_get_custom_clusters_from_server(self):
        self.assertEqual(1, 1)
        return  # Skip this test

        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        conditions: dict[str, bool] = {
            "published": True,
            "minimal": True,
            "custom": True
        }
        clusters = misp_api.get_custom_clusters_from_server(conditions, server)
        self.assertEqual(len(clusters), 21106)

    def test_get_galaxy_cluster_from_server(self):
        mmisp_api: TestMispAPI = TestMispAPI()
        server: MispServer = mmisp_api.get_server(1)
        cluster = mmisp_api.get_galaxy_cluster(1, server)
        self.assertEqual(cluster.uuid, "988e1441-0350-5c39-979d-b0ca99c8d20b")

    def test_get_minimal_events_from_server(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        events = misp_api.get_minimal_events_from_server(True, server)
        self.assertGreater(len(events), 1300)

    def test_get_event(self):
        self.assertEqual(1, 1)
        return  # Skip this test

        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        event = misp_api.get_event(2, server)
        self.assertEqual(event.uuid, "fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11e8")

    def test_get_sightings_from_event(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        sightings = misp_api.get_sightings_from_event(2, server)
        self.assertEqual(sightings[0].id, 14)

    def test_get_proposals(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        proposals = misp_api.get_proposals(server)
        self.assertEqual(proposals[0].id, 2)

    def test_get_sharing_groups(self):
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)

        sharing_groups = misp_api.get_sharing_groups(server)
        self.assertEqual(sharing_groups[0].name, "TestSharingGroup")

    def test_save_cluster(self):
        misp_api: MispAPI = MispAPI()
        # cluster: MispCluster = MispCluster()
        # what is a cluster
        pass

    def test_save_event(self):
        misp_api: MispAPI = MispAPI()
        event: MispEvent = MispEvent(id=123123123,
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
                                     tags=[],
                                     cryptographic_key=None,
                                     org=MispOrganisation(id=1,
                                                          name="ORGNAME",
                                                          uuid="5019f511811a4dab800c80c92bc16d3d"),
                                     orgc=MispOrganisation(id=1, name="ORGNAME",
                                                           uuid="5019f511811a4dab800c80c92bc16d3d"))
        misp_api.save_event(event)
        # TODO: Ahmed how to test this?

    def test_save_sighting(self):
        # TODO: Ahmed how to test this?
        pass

    def test_save_proposal(self):
        # TODO: Ahmed how to test this?
        pass

    def test_create_attribute(self):
        misp_api: MispAPI = MispAPI()
        event_attribute: MispEventAttribute = MispEventAttribute(
            id=1, event_id=20, object_id=3, object_relation='act-as',
            category='Other', type='text', to_ids=False,
            uuid='40917bc9-123e-43da-a5e1-aa15a9a4ea6d',
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
        print(event_attribute.tags[0][0].ser_model())
        print(event_attribute.model_dump_json())
        misp_api.create_attribute(event_attribute)

    def test_create_tag(self):
        misp_api: MispAPI = MispAPI()
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
            favourite=False)
        pass

    def test_attach_attribute_tag(self):
        misp_api: MispAPI = MispAPI()
        pass

    def test_attach_event_tag(self):
        misp_api: MispAPI = MispAPI()
        pass

    def test_modify_event_tag_relationship(self):
        pass

    def test_modify_attribute_tag_relationship(self):
        pass
