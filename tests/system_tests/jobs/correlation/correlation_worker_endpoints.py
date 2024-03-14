from unittest import TestCase

import requests

from pydantic import json
from requests import Response

from tests.system_tests.request_settings import url, headers


class TestCorrelationWorkerRouter(TestCase):

    def test_change_threshold(self):
        body: json = {"user": {"user_id": 66}, "data": {"new_threshold": 25}}
        expected_output: json = {"saved": True, "valid_threshold": True, "new_threshold": 25}

        response: Response = requests.put(url + "/worker/correlation/changeThreshold", json=body, headers=headers)
        self.assertEqual(response.json(), expected_output)

        body = {"user": {"user_id": 66}, "data": {"new_threshold": 20}}
        expected_output = {"saved": True, "valid_threshold": True, "new_threshold": 20}

        response = requests.put(url + "/worker/correlation/changeThreshold", json=body, headers=headers)
        self.assertEqual(response.json(), expected_output)

    def test_get_threshold(self):
        expected_output: json = {20}

        response: Response = requests.get(url + "/worker/correlation/threshold", headers=headers)
        self.assertEqual(response.json(), expected_output)


