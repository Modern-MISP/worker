
from unittest import TestCase

import requests
import time
import json

from tests.system_tests.request_settings import url, headers


class TestCorrelationJobs(TestCase):

    def __enable_worker(self):
        response: dict = requests.post(url + "/worker/correlation/enable", headers=headers).json()
        expected: json = {"success": True, "message": "Correlation-Worker now enabled",
                          "url": "/worker/correlation/enable"}
        expected_already_enabled: json = {"success": False, "message": "Correlation-Worker already enabled",
                                          "url": "/worker/correlation/enable"}
        if response["success"]:
            self.assertEqual(response, expected)
        else:
            self.assertEqual(response, expected_already_enabled)

    def check_status(self, response) -> str:
        job_id: str = response["job_id"]
        self.assertEqual(response["success"], True)
        ready: bool = False
        count: int = 0
        while not ready:
            count += 1
            print(count/2)
            request = requests.get(url + f"/job/{job_id}/status", headers=headers)
            response = request.json()

            self.assertEqual(request.status_code, 200)

            if response["status"] == "success":
                ready = True
                self.assertEqual(response["status"], "success")
                self.assertEqual(response["message"], "Job is finished")

            time.sleep(0.5)
        return job_id

    def test_correlate_value(self):
        self.__enable_worker()
        body: json = {"user": {"user_id": 66}, "data": {"value": "test"}}

        response: dict = requests.post(url + "/job/correlateValue", json=body, headers=headers).json()
        job_id = self.check_status(response)

        response = requests.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertTrue(response["success"])
        self.assertTrue(response["found_correlations"])
        self.assertFalse(response["is_excluded_value"])
        self.assertFalse(response["is_over_correlating_value"])
        self.assertIsNone(response["plugin_name"])
        self.assertIsNotNone(response["events"])

    def test_plugin_list(self):
        response: list[dict] = requests.get(url + "/worker/correlation/plugins", headers=headers).json()
        test_plugin = response[0]
        expected_plugin = {"NAME": "CorrelationTestPlugin", "PLUGIN_TYPE": "correlation",
                           "DESCRIPTION": "This is a plugin to test the correlation plugin integration.",
                           "AUTHOR": "Tobias Gasteiger", "VERSION": "1.0", "CORRELATION_TYPE": "all"}
        self.assertEqual(test_plugin, expected_plugin)

    def test_regenerate_occurrences(self):
        self.__enable_worker()
        body: json = {"user_id": 66}
        response: dict = requests.post(url + "/job/regenerateOccurrences", json=body, headers=headers).json()
        job_id: str = self.check_status(response)

        response = requests.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertTrue(response["success"])
        self.assertIsInstance(response["database_changed"], bool)
