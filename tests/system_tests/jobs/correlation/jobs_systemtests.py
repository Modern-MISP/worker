
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
        count: float = 0
        times: int = 0
        timer: float = 0.5
        while not ready:
            times += 1
            count += timer
            print(f"Time: {count}")
            request = requests.get(url + f"/job/{job_id}/status", headers=headers)
            response = request.json()

            self.assertEqual(request.status_code, 200)

            if response["status"] == "success":
                ready = True
                self.assertEqual(response["status"], "success")
                self.assertEqual(response["message"], "Job is finished")
            if response["status"] == "failed":
                self.fail(response["message"])

            if times % 10 == 0 and times != 0:
                timer *= 2
            time.sleep(timer)
        print("Job is finished")
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

    def test_regenerate_occurrences(self) -> bool:
        self.__enable_worker()
        body: json = {"user_id": 66}
        response: dict = requests.post(url + "/job/regenerateOccurrences", json=body, headers=headers).json()
        job_id: str = self.check_status(response)

        response = requests.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertTrue(response["success"])
        self.assertIsInstance(response["database_changed"], bool)
        print(response["database_changed"])
        return response["database_changed"]

    def test_regenerate_occurrences_twice(self):
        first: bool = self.test_regenerate_occurrences()
        print(f"first is finished: {first}")
        second: bool = self.test_regenerate_occurrences()
        self.assertFalse(second)

    def test_top_correlations(self):
        self.__enable_worker()
        body: json = {"user_id": 66}
        response: dict = requests.post(url + "/job/topCorrelations", json=body, headers=headers).json()
        job_id: str = self.check_status(response)

        response = requests.get(url + f"/job/{job_id}/result", headers=headers).json()
        result = response["top_correlations"]

        self.assertTrue(response["success"])
        self.assertIsInstance(result, list)
        self.assertIsNotNone(result)
        last: int = 1000000000000000000000000
        summary: int = 0
        for res in result:
            self.assertNotEqual(0, res[1])
            self.assertGreaterEqual(last, res[1])
            last = res[1]
            print(res)
            summary += res[1]
        print(summary)
        print(len(result))

