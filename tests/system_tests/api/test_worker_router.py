from unittest import TestCase

import requests

from pydantic import json

from mmisp.worker.api.worker_router.input_data import WorkerEnum

url = "http://localhost:5000/"
headers = {"Authorization": "Bearer 1409"}


class TestWorkerRouter(TestCase):
    def test_enable_workers(self):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            responses.append(requests.post(url + f"worker/{name}/enable", headers=headers).json())
            expected_output.append({"success": True,
                                    "message": f"{name.capitalize()}-Worker now enabled",
                                    "url": f"/worker/{name}/enable"})
            requests.post(url + f"worker/{name}/disable", headers=headers)

        self.assertEqual(responses, expected_output)

    def test_disable_workers(self):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"worker/{name}/enable", headers=headers).json()
            responses.append(requests.post(url + f"worker/{name}/disable", headers=headers).json())
            expected_output.append({"success": True,
                                    "message": f"{name.capitalize()}-Worker stopped successfully",
                                    "url": f"/worker/{name}/disable"})

        self.assertEqual(responses, expected_output)

    def test_worker_status_idle(self):

        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"worker/{name}/enable", headers=headers).json()
            responses.append(requests.get(url + f"worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "idle",
                                    "jobs_queued": 0})

        self.assertEqual(responses, expected_output)

    def test_worker_status_deactivated(self):

        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"worker/{name}/disable", headers=headers).json()
            responses.append(requests.get(url + f"worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "deactivated",
                                    "jobs_queued": 0})

        self.assertEqual(responses, expected_output)

