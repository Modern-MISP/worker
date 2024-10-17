import subprocess
from time import sleep

from pydantic import json

from mmisp.worker.api.requests_schemas import WorkerEnum
from mmisp.worker.controller import celery_client, worker_controller
from tests.system_tests.request_settings import headers
from tests.system_tests.utility import check_status

_dummy_body: json = {
    "user": {"user_id": 3},
    "data": {"attribute_id": 272910, "enrichment_plugins": ["Blocking Plugin"]},
}


def test_get_job_status_success(client):
    data: json = {"user": {"user_id": 3}, "data": {"attribute_id": 272910, "enrichment_plugins": []}}

    request = client.post("/job/enrichAttribute", headers=headers, json=data)

    assert (request.status_code == 200), "Job could not be created"
    assert check_status(client, headers, request.json()["job_id"])


def test_get_job_status_failed(client):
    body: json = {
        "user": {"user_id": 1},
        "data": {"post_id": -69, "title": "test", "message": "test message", "receiver_ids": [-69]},
    }

    request = client.post("/job/postsEmail", json=body, headers=headers)

    assert (request.status_code == 200), "Job could not be created"

    job_id: int = request.json()["job_id"]

    sleep(3)

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "Job failed during execution", "status": "failed"}

    assert expected_output == response


def test_get_job_status_inProgress(client):
    worker_controller.pause_all_workers()

    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    assert (request.status_code == 200), "Job could not be created"

    job_id: int = request.json()["job_id"]

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "Job is currently being executed", "status": "inProgress"}
    worker_controller.reset_worker_queues()

    # to ensure that the job is finished and the worker is free again for other tests
    assert check_status(client, headers, job_id)
    assert expected_output == response


def test_get_job_status_queued(client):
    worker_controller.pause_all_workers()

    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    assert (request.status_code == 200), "Job could not be created"

    job_id: int = request.json()["job_id"]

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "Job is currently enqueued", "status": "queued"}

    worker_controller.reset_worker_queues()

    # to ensure that the job is finished and the worker is free again for other tests
    assert check_status(client, headers, job_id)
    assert expected_output == response


def test_get_job_status_revoked_worker_enabled(client):
    client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    assert (request.status_code == 200), "Job could not be created"

    job_id: int = request.json()["job_id"]

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=headers)

    assert (cancel_resp.status_code == 200), "Job could not be created"

    sleep(4)

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "The job was canceled before it could be processed", "status": "revoked"}

    assert expected_output == response


def test_get_job_status_revoked_worker_disabled(client):
    worker_controller.pause_all_workers()
    # one worker has to be enabled to ensure that the job will be canceled
    subprocess.Popen(
        f"celery -A {celery_client.__name__} worker -Q {WorkerEnum.SEND_EMAIL.value} "
        f"--loglevel=info -n {WorkerEnum.SEND_EMAIL.value}@%h --concurrency 1",
        shell=True,
    )

    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    assert (request.status_code == 200), "Job could not be created"

    sleep(1)

    job_id: int = request.json()["job_id"]

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=headers)

    assert (cancel_resp.status_code == 200), "Job could not be created"

    worker_controller.reset_worker_queues()

    response: json = client.get(f"/job/{job_id}/status", headers=headers).json()

    expected_output = {"message": "The job was canceled before it could be processed", "status": "revoked"}

    assert expected_output == response


def test_remove_job(client):
    worker_controller.pause_all_workers()

    client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)
    request = client.post("/job/enrichAttribute", headers=headers, json=_dummy_body)

    assert (request.status_code == 200), "Job could not be created"

    job_id: int = request.json()["job_id"]

    worker_controller.reset_worker_queues()

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=headers)

    assert (request.status_code == 200), "Job could not be created"

    expected_output = {"success": True}

    assert expected_output == cancel_resp.json()
