from time import sleep
from unittest import TestCase

import requests

from pydantic import json

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from tests.system_tests.request_settings import url, headers
from tests.system_tests.utility import check_status


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
            assert requests.get(url + f"/worker/{name}/status", headers=headers).json()["jobs_queued"] == 0, \
                "Worker queue is not empty"
            responses.append(requests.get(url + f"/worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "idle",
                                    "jobs_queued": 0})

        self.assertEqual(expected_output, responses)

    def test_worker_status_deactivated(self):

        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            requests.post(url + f"/worker/{name}/disable", headers=headers).json()
            assert requests.get(url + f"/worker/{name}/status", headers=headers).json()["jobs_queued"] == 0, \
                "Worker queue is not empty"
            responses.append(requests.get(url + f"/worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "deactivated",
                                    "jobs_queued": 0})

        self.assertEqual(expected_output, responses)

    def test_worker_status_working(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {
                "user_id": 3
            },
            "data": {
                "attribute_id": 272910,
                "enrichment_plugins": ["Blocking Plugin"]
            }
        }

        request = requests.post(url + "/job/enrichAttribute", headers=headers, json=data)

        if request.status_code != 200:
            self.fail("Job could not be created")

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        sleep(3)

        response: json = requests.get(url + "/worker/enrichment/status", headers=headers).json()

        # to ensure that the job is finished and the worker is free again for other tests
        self.assertTrue(check_status(request.json()["job_id"]))

        self.assertEqual("working", response["status"])

    def test_worker_status_working_multiple_jobs_queued(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {
                "user_id": 3
            },
            "data": {
                "attribute_id": 272910,
                "enrichment_plugins": ["Blocking Plugin"]
            }
        }

        job_ids: list[int] = []

        for _ in range(3):
            request = requests.post(url + "/job/enrichAttribute", headers=headers, json=data)
            job_ids.append(request.json()["job_id"])
            if request.status_code != 200:
                self.fail("Job could not be created")

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        sleep(3)

        response: json = requests.get(url + "/worker/enrichment/status", headers=headers).json()

        # to ensure that the job is finished and the worker is free again for other tests
        for job_id in job_ids:
            self.assertTrue(check_status(job_id))

        self.assertEqual(2, response["jobs_queued"])

    def test_worker_status_deactivated_multiple_jobs_queued(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {
                "user_id": 4
            },
            "data": {
                "attribute_id": 272910,
                "enrichment_plugins": ["Blocking Plugin"]
            }
        }

        job_ids: list[int] = []

        for _ in range(3):
            request = requests.post(url + "/job/enrichAttribute", headers=headers, json=data)
            job_ids.append(request.json()["job_id"])
            if request.status_code != 200:
                self.fail("Job could not be created")

        sleep(1)

        response: json = requests.get(url + "/worker/enrichment/status", headers=headers).json()

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        # to ensure that the job is finished and the worker is free again for other tests
        for job_id in job_ids:
            self.assertTrue(check_status(job_id))

        self.assertEqual(3, response["jobs_queued"])
