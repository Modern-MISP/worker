from time import sleep
from unittest import TestCase

import requests

from pydantic import json

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from tests.system_tests.request_settings import url, headers


class TestWorkerRouter(TestCase):
    def test_enable_workers(self):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"/worker/{name}/disable", headers=headers)
            responses.append(requests.post(url + f"/worker/{name}/enable", headers=headers).json())
            expected_output.append({"success": True,
                                    "message": f"{name.capitalize()}-Worker now enabled",
                                    "url": f"/worker/{name}/enable"})

        self.assertEqual(expected_output, responses)

    def test_workers_already_enabled(self):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"/worker/{name}/enable", headers=headers)
            responses.append(requests.post(url + f"/worker/{name}/enable", headers=headers).json())
            expected_output.append({"success": False,
                                    "message": f"{name.capitalize()}-Worker already enabled",
                                    "url": f"/worker/{name}/enable"})

        self.assertEqual(expected_output, responses)

    def test_disable_workers(self):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"/worker/{name}/enable", headers=headers).json()
            responses.append(requests.post(url + f"/worker/{name}/disable", headers=headers).json())
            expected_output.append({"success": True,
                                    "message": f"{name.capitalize()}-Worker stopped successfully",
                                    "url": f"/worker/{name}/disable"})

        self.assertEqual(expected_output, responses)

    def test_worker_status_idle(self):

        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"/worker/{name}/enable", headers=headers).json()
            responses.append(requests.get(url + f"/worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "idle",
                                    "jobs_queued": 0})

        self.assertEqual(expected_output, responses)

    def test_worker_status_deactivated(self):

        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"/worker/{name}/disable", headers=headers).json()
            responses.append(requests.get(url + f"/worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "deactivated",
                                    "jobs_queued": 0})

        self.assertEqual(expected_output, responses)

    def test_worker_status_working(self):
        requests.post(url + f"/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {
                "user_id": 3
            },
            "data": {
                "attribute_id": 272910,
                "enrichment_plugins": ["Blocking Plugin"]
            }
        }

        request = requests.post(url + f"/job/enrichAttribute", headers=headers, json=data)

        if request.status_code != 200:
            self.fail("Job could not be created")

        requests.post(url + f"/worker/enrichment/enable", headers=headers)

        sleep(3)

        response: json = requests.get(url + f"/worker/enrichment/status", headers=headers).json()

        self.assertEqual("working", response["status"])

    def test_worker_status_working_multiple_jobs_queued(self):
        requests.post(url + f"/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {
                "user_id": 3
            },
            "data": {
                "attribute_id": 272910,
                "enrichment_plugins": ["Blocking Plugin"]
            }
        }

        for i in range(5):
            request = requests.post(url + f"/job/enrichAttribute", headers=headers, json=data)

        if request.status_code != 200:
            self.fail("Job could not be created")

        requests.post(url + f"/worker/enrichment/enable", headers=headers)

        sleep(3)

        response: json = requests.get(url + f"/worker/enrichment/status", headers=headers).json()

        self.assertEqual(4, response["jobs_queued"])

    def test_worker_status_deactivated_multiple_jobs_queued(self):
        requests.post(url + f"/worker/enrichment/disable", headers=headers)

        amount_of_jobs: int = requests.get(url + f"/worker/enrichment/status", headers=headers).json()["jobs_queued"]

        data: json = {
            "user": {
                "user_id": 3
            },
            "data": {
                "attribute_id": 272910,
                "enrichment_plugins": ["Blocking Plugin"]
            }
        }

        for i in range(5):
            request = requests.post(url + f"/job/enrichAttribute", headers=headers, json=data)

        if request.status_code != 200:
            self.fail("Job could not be created")

        sleep(3)

        response: json = requests.get(url + f"/worker/enrichment/status", headers=headers).json()

        self.assertEqual(5 + amount_of_jobs, response["jobs_queued"])
