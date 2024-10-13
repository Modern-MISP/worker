from time import sleep

from pydantic import json

from mmisp.worker.api.worker_router.input_data import WorkerEnum
from tests.system_tests.request_settings import headers
from tests.system_tests.utility import check_status


def test_enable_workers(client, init_api_config):
    print("bonobo test_enable_workers")
    responses: list[json] = []
    expected_output: list[json] = []

    for name in WorkerEnum:
        client.post(f"/worker/{name}/disable", headers=headers)
        responses.append(client.post(f"/worker/{name}/enable", headers=headers).json())
        expected_output.append(
            {"success": True, "message": f"{name.capitalize()}-Worker now enabled", "url": f"/worker/{name}/enable"}
        )

    assert expected_output == responses


def test_workers_already_enabled(client, init_api_config):
    print("bonobo test_workers_already_enabled")
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

    assert expected_output == responses


def test_disable_workers(client, init_api_config):
    print("bonobo test_disable_workers")
    responses: list[json] = []
    expected_output: list[json] = []

    for name in WorkerEnum:
        client.post(f"/worker/{name}/enable", headers=headers).json()
        responses.append(client.post(f"/worker/{name}/disable", headers=headers).json())
        expected_output.append(
            {
                "success": True,
                "message": f"{name.capitalize()}-Worker stopped successfully",
                "url": f"/worker/{name}/disable",
            }
        )
    assert expected_output == responses


def test_worker_status_idle(client, init_api_config):
    print("bonobo test_worker_status_idle")
    responses: list[json] = []
    expected_output: list[json] = []

    for name in WorkerEnum:
        client.post(f"/worker/{name}/enable", headers=headers).json()
        assert (
            client.get(f"/worker/{name}/status", headers=headers).json()["jobs_queued"] == 0
        ), "Worker queue is not empty"
        responses.append(client.get(f"/worker/{name}/status", headers=headers).json())
        expected_output.append({"status": "idle", "jobs_queued": 0})

    assert expected_output == responses


def test_worker_status_deactivated(client, init_api_config):
    print("bonobo test_worker_status_deactivated")
    responses: list[json] = []
    expected_output: list[json] = []

    for name in WorkerEnum:
        client.post(f"/worker/{name}/disable", headers=headers).json()
        assert (
            client.get(f"/worker/{name}/status", headers=headers).json()["jobs_queued"] == 0
        ), "Worker queue is not empty"
        responses.append(client.get(f"/worker/{name}/status", headers=headers).json())
        expected_output.append({"status": "deactivated", "jobs_queued": 0})

    assert expected_output == responses


def test_worker_status_working(client, init_api_config):
    print("bonobo test_worker_status_working")
    assert (
        client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    client.post("/worker/enrichment/disable", headers=headers)

    data: json = {
        "user": {"user_id": 3},
        "data": {"attribute_id": 272910, "enrichment_plugins": ["Blocking Plugin"]},
    }

    request = client.post("/job/enrichAttribute", headers=headers, json=data)

    assert request.status_code == 200

    client.post("/worker/enrichment/enable", headers=headers)

    sleep(3)

    response: json = client.get("/worker/enrichment/status", headers=headers).json()

    # to ensure that the job is finished and the worker is free again for other tests
    assert bool(check_status(request.json()["job_id"], client))

    assert "working" == response["status"]


def test_worker_status_working_multiple_jobs_queued(client, init_api_config):
    print("bonobo test_worker_status_working_multiple_jobs_queued")
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
        assert request.status_code == 200

    client.post("/worker/enrichment/enable", headers=headers)

    sleep(3)

    response: json = client.get("/worker/enrichment/status", headers=headers).json()

    # to ensure that the job is finished and the worker is free again for other tests
    for job_id in job_ids:
        assert bool(check_status(job_id, client))

    assert 2 == response["jobs_queued"]


def test_worker_status_deactivated_multiple_jobs_queued(client, init_api_config):
    print("bonobo test_worker_status_deactivated_multiple_jobs_queued")
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
        assert request.status_code == 200

    sleep(1)

    response: json = client.get("/worker/enrichment/status", headers=headers).json()

    client.post("/worker/enrichment/enable", headers=headers)

    # to ensure that the job is finished and the worker is free again for other tests
    for job_id in job_ids:
        assert bool(check_status(job_id, client))

    assert 3 == response["jobs_queued"]
