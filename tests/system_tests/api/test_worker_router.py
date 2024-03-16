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

    def test_worker_status_active(self):
        #todo waiting for amadeus
        pass

