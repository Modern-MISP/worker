from unittest import TestCase

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_server import MispServer


class TestBasicApiEndpoints(TestCase):
    def test_get_server(self):
        misp_api: MispAPI = MispAPI()
        server: MispServer = misp_api.get_server(1)
        self.assertEqual(server.name, "MISP 02")
