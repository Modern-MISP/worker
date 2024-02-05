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
        misp_api: TestMispAPI = TestMispAPI()
        server: MispServer = misp_api.get_server(1)
        conditions: dict[str, bool] = {
            "published": True,
            "minimal": True,
            "custom": True
        }
        clusters = misp_api.get_custom_clusters_from_server(conditions, server)
        print(len(clusters))
        self.assertEqual(len(clusters), 21106)
