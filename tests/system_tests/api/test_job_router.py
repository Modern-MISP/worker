from time import sleep

from pydantic import json

from mmisp.worker.controller import worker_controller
from tests.system_tests.request_settings import headers
from tests.system_tests.utility import check_status

_dummy_body: json = {
    "user": {"user_id": 3},
    "data": {"attribute_id": 272910, "enrichment_plugins": ["Blocking Plugin"]},
}


def test_get_job_status_success(client):
    response = client.get("/worker/enrichment/status", headers=headers).json()
    print("bonobo", response)
    assert (
        client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    data: json = {"user": {"user_id": 3}, "data": {"attribute_id": 272910, "enrichment_plugins": []}}

    request = client.post("/job/enrichAttribute", headers=headers, json=data)

    if request.status_code != 200:
        print("Job could not be created")
        assert False

    assert check_status(client, request.json()["job_id"], headers)


def test_get_job_status_failed(client):
    assert (
        client.get("/worker/sendEmail/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    body: json = {
        "user": {"user_id": 1},
        "data": {"post_id": -69, "title": "test", "message": "test message", "receiver_ids": [-69]},
    }

    request = client.post("/job/postsEmail", json=body, headers=headers)
    if request.status_code != 200:
        print("Job could not be created")
        assert False

    job_id: int = request.json()["job_id"]

    sleep(3)

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "Job failed during execution", "status": "failed"}

    assert expected_output == response


def test_get_job_status_inProgress(client):
    assert (
        client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    worker_controller.pause_all_workers()

    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    if request.status_code != 200:
        print("Job could not be created")
        assert False

    job_id: int = request.json()["job_id"]

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "Job is currently being executed", "status": "inProgress"}
    worker_controller.reset_worker_queues()

    # to ensure that the job is finished and the worker is free again for other tests
    assert check_status(client, headers, job_id)
    assert expected_output == response


def test_get_job_status_queued(client):
    assert (
        client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    worker_controller.pause_all_workers()

    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    if request.status_code != 200:
        print("Job could not be created")
        assert False

    job_id: int = request.json()["job_id"]

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "Job is currently enqueued", "status": "queued"}

    worker_controller.reset_worker_queues()

    # to ensure that the job is finished and the worker is free again for other tests
    assert check_status(client, headers, job_id)

    assert expected_output == response


def test_get_job_status_revoked_worker_enabled(client):
    assert (
        client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)
    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    if request.status_code != 200:
        print("Job could not be created")
        assert False

    job_id: int = request.json()["job_id"]

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=headers)

    if cancel_resp.status_code != 200:
        print("Job could not be canceled")
        assert False

    sleep(4)

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "The job was canceled before it could be processed", "status": "revoked"}

    assert expected_output == response


def test_get_job_status_revoked_worker_disabled(client):
    assert (
        client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    # one worker has to be enabled to ensure that the job will be canceled
    worker_controller.pause_all_workers()

    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    if request.status_code != 200:
        print("Job could not be created")
        assert False

    sleep(1)

    job_id: int = request.json()["job_id"]

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=headers)

    if cancel_resp.status_code != 200:
        print("Job could not be created")
        assert False

    worker_controller.reset_worker_queues()

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "The job was canceled before it could be processed", "status": "revoked"}

    assert expected_output == response


def test_remove_job(client):
    assert (
        client.get("/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0
    ), "Worker queue is not empty"

    worker_controller.pause_all_workers()

    client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)
    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    if request.status_code != 200:
        print("Job could not be created")
        assert False

    job_id: int = request.json()["job_id"]

    worker_controller.reset_worker_queues()

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=headers)

    if cancel_resp.status_code != 200:
        print("Job could not be created")
        assert False

    expected_output = {"success": True}

    assert expected_output == cancel_resp.json()
