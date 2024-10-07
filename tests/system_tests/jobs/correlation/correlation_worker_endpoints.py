from typing import Self
from unittest import TestCase

from fastapi.testclient import TestClient
from pydantic import json
from requests import Response

from tests.system_tests.request_settings import headers


class TestCorrelationWorkerRouter(TestCase):
    def test_change_threshold(self: Self, client: TestClient):
        body: json = {"user": {"user_id": 66}, "data": {"new_threshold": 25}}
        expected_output: json = {"saved": True, "valid_threshold": True, "new_threshold": 25}

        response: Response = client.put("/worker/correlation/changeThreshold", json=body, headers=headers)
        self.assertEqual(response.json(), expected_output)

        body = {"user": {"user_id": 66}, "data": {"new_threshold": 20}}
        expected_output = {"saved": True, "valid_threshold": True, "new_threshold": 20}

        response = client.put("/worker/correlation/changeThreshold", json=body, headers=headers)
        self.assertEqual(response.json(), expected_output)

    def test_get_threshold(self: Self, client: TestClient):
        expected_output: json = {20}

        response: Response = client.get("/worker/correlation/threshold", headers=headers)
        self.assertEqual(response.json(), expected_output)
