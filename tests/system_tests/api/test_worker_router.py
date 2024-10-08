from time import sleep
from typing import Self
from unittest import TestCase

from fastapi.testclient import TestClient
from pydantic import json

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from tests.system_tests.request_settings import headers
from tests.system_tests.utility import check_status


class TestWorkerRouter(TestCase):
    def test_enable_workers(self: Self, client: TestClient):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            client.post(f"/worker/{name}/disable", headers=headers)
            responses.append(client.post(f"/worker/{name}/enable", headers=headers).json())
            expected_output.append(
                {"success": True, "message": f"{name.capitalize()}-Worker now enabled", "url": f"/worker/{name}/enable"}
            )

        self.assertEqual(expected_output, responses)

    def test_workers_already_enabled(self: Self, client: TestClient):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            client.post(f"/worker/{name}/enable", headers=headers)
            responses.append(client.post(f"/worker/{name}/enable", headers=headers).json())
            expected_output.append(
                {
                    "success": False,
                    "message": f"{name.capitalize()}-Worker already enabled",
                    "url": f"/worker/{name}/enable",
                }
            )

        self.assertEqual(expected_output, responses)

    def test_disable_workers(self: Self, client: TestClient):
        print(1)
        responses: list[json] = []
        print(2)
        expected_output: list[json] = []
        print(3)
        for name in WorkerEnum:
            print(4)
            client.post(f"/worker/{name}/enable", headers=headers).json()
            print(5)
            responses.append(client.post(f"/worker/{name}/disable", headers=headers).json())
            print(6)
            expected_output.append(
                {
                    "success": True,
                    "message": f"{name.capitalize()}-Worker stopped successfully",
                    "url": f"/worker/{name}/disable",
                }
            )
            print(7)

        self.assertEqual(expected_output, responses)

    def test_worker_status_idle(self: Self, client: TestClient):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            client.post(f"/worker/{name}/enable", headers=headers).json()
            assert (
                client.get(f"/worker/{name}/status", headers=headers).json()["jobs_queued"] == 0
            ), "Worker queue is not empty"
            responses.append(client.get(f"/worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "idle", "jobs_queued": 0})

        self.assertEqual(expected_output, responses)

    def test_worker_status_deactivated(self: Self, client: TestClient):
        responses: list[json] = []
        expected_output: list[json] = []

        for name in WorkerEnum:
            client.post(f"/worker/{name}/disable", headers=headers).json()
            assert (
                client.get(f"/worker/{name}/status", headers=headers).json()["jobs_queued"] == 0
            ), "Worker queue is not empty"
            responses.append(client.get(f"/worker/{name}/status", headers=headers).json())
            expected_output.append({"status": "deactivated", "jobs_queued": 0})

        self.assertEqual(expected_output, responses)

    def test_worker_status_working(self: Self, client: TestClient):
        assert (
            client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
        ), "Worker queue is not empty"

        client.post("/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {"user_id": 3},
            "data": {"attribute_id": 272910, "enrichment_plugins": ["Blocking Plugin"]},
        }

        request = client.post("/job/enrichAttribute", headers=headers, json=data)

        if request.status_code != 200:
            self.fail("Job could not be created")

        client.post("/worker/enrichment/enable", headers=headers)

        sleep(3)

        response: json = client.get("/worker/enrichment/status", headers=headers).json()

        # to ensure that the job is finished and the worker is free again for other tests
        self.assertTrue(check_status(request.json()["job_id"], client))

        self.assertEqual("working", response["status"])

    def test_worker_status_working_multiple_jobs_queued(self: Self, client: TestClient):
        assert (
            client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
        ), "Worker queue is not empty"

        client.post("/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {"user_id": 3},
            "data": {"attribute_id": 272910, "enrichment_plugins": ["Blocking Plugin"]},
        }

        job_ids: list[int] = []

        for _ in range(3):
            request = client.post("/job/enrichAttribute", headers=headers, json=data)
            job_ids.append(request.json()["job_id"])
            if request.status_code != 200:
                self.fail("Job could not be created")

        client.post("/worker/enrichment/enable", headers=headers)

        sleep(3)

        response: json = client.get("/worker/enrichment/status", headers=headers).json()

        # to ensure that the job is finished and the worker is free again for other tests
        for job_id in job_ids:
            self.assertTrue(check_status(job_id, client))

        self.assertEqual(2, response["jobs_queued"])

    def test_worker_status_deactivated_multiple_jobs_queued(self: Self, client: TestClient):
        assert (
            client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
        ), "Worker queue is not empty"

        client.post("/worker/enrichment/disable", headers=headers)

        data: json = {
            "user": {"user_id": 4},
            "data": {"attribute_id": 272910, "enrichment_plugins": ["Blocking Plugin"]},
        }

        job_ids: list[int] = []

        for _ in range(3):
            request = client.post("/job/enrichAttribute", headers=headers, json=data)
            job_ids.append(request.json()["job_id"])
            if request.status_code != 200:
                self.fail("Job could not be created")

        sleep(1)

        response: json = client.get("/worker/enrichment/status", headers=headers).json()

        client.post("/worker/enrichment/enable", headers=headers)

        # to ensure that the job is finished and the worker is free again for other tests
        for job_id in job_ids:
            self.assertTrue(check_status(job_id, client))

        self.assertEqual(3, response["jobs_queued"])
