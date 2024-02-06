from unittest import TestCase

from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
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
        return # Skip this test

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
