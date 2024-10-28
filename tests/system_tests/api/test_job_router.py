from time import sleep

import pytest_asyncio
from pydantic import json
from starlette.testclient import TestClient

from mmisp.tests.generators.model_generators.attribute_generator import generate_attribute
from mmisp.worker.controller import worker_controller
from tests.plugins.enrichment_plugins.blocking_plugin import BlockingPlugin
from tests.system_tests.utility import check_status

from ...plugins.enrichment_plugins.blocking_plugin import BlockingPlugin


@pytest_asyncio.fixture()
async def attribute_matching_blocking_plugin(db, event):
    attribute = generate_attribute(event_id=event.id)
    attribute.value = BlockingPlugin.PLUGIN_INFO.MISP_ATTRIBUTES.INPUT[0]

    event.attribute_count += 1

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute
    await db.refresh(event)

    await db.delete(attribute)
    event.attribute_count -= 1
    await db.commit()


def test_get_job_status_success(client: TestClient, authorization_headers, user, attribute_matching_blocking_plugin):
    data: json = {"user": {"user_id": user.id}, "data": {"attribute_id": attribute_matching_blocking_plugin.id,
                                                         "enrichment_plugins": []}}

    request = client.post("/job/enrichAttribute", headers=authorization_headers, json=data)

    assert request.status_code == 200, "Job could not be created"
    assert check_status(client, authorization_headers, request.json()["job_id"])


def test_get_job_status_failed(client: TestClient, authorization_headers, user):
    body: json = {
        "user": {"user_id": user.id},
        "data": {"post_id": -69, "title": "test", "message": "test message", "receiver_ids": [-69]},
    }

    request = client.post("/job/postsEmail", json=body, headers=authorization_headers)

    assert request.status_code == 200, "Job could not be created"

    job_id: int = request.json()["job_id"]

    check_status(client, authorization_headers, request.json()["job_id"])

    response: json = client.get(f"/job/{job_id}/status", headers=authorization_headers).json()

    expected_output = {"message": "Job failed during execution", "status": "failed"}

    assert expected_output == response


def test_get_job_status_in_progress(
    client: TestClient, authorization_headers, user, attribute_matching_blocking_plugin):
    worker_controller.pause_all_workers()

    dummy_body = _get_dummy_body(user.id, attribute_matching_blocking_plugin.id)

    request = client.post("/job/enrichAttribute", headers=authorization_headers, json=dummy_body)

    assert request.status_code == 200, "Job could not be created"

    job_id: int = request.json()["job_id"]

    response: json = client.get(f"/job/{job_id}/status", headers=authorization_headers).json()

    expected_output = {"message": "Job is currently being executed", "status": "inProgress"}
    worker_controller.reset_worker_queues()

    print("bonobo: status1: ", response)

    r = client.get(f"/job/{job_id}/status", headers=authorization_headers)

    print("bonobo: status2: ", r.json())

    # to ensure that the job is finished and the worker is free again for other tests
    assert check_status(client, authorization_headers, job_id)
    assert expected_output == response


def test_get_job_status_queued(client: TestClient, authorization_headers, user, attribute_matching_blocking_plugin):
    worker_controller.pause_all_workers()

    dummy_body = _get_dummy_body(user.id, attribute_matching_blocking_plugin.id)

    request = client.post("/job/enrichAttribute", headers=authorization_headers, json=dummy_body)

    assert request.status_code == 200, "Job could not be created"

    job_id: int = request.json()["job_id"]

    response: json = client.get(f"/job/{job_id}/status", headers=authorization_headers).json()

    expected_output = {"message": "Job is currently enqueued", "status": "queued"}

    worker_controller.reset_worker_queues()

    # to ensure that the job is finished and the worker is free again for other tests
    assert check_status(client, authorization_headers, job_id)
    assert expected_output == response


def test_get_job_status_revoked_worker_enabled(
    client: TestClient, authorization_headers, user, attribute_matching_blocking_plugin
):
    dummy_body = _get_dummy_body(user.id, attribute_matching_blocking_plugin.id)

    request = client.post("/job/enrichAttribute", headers=authorization_headers, json=dummy_body)

    assert request.status_code == 200, "Job could not be created"

    job_id: int = request.json()["job_id"]

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=authorization_headers)

    assert cancel_resp.status_code == 200, "Job could not be created"

    sleep(4)

    response: json = client.get(f"/job/{job_id}/status", headers=authorization_headers).json()

    expected_output = {"message": "The job was canceled before it could be processed", "status": "revoked"}

    assert expected_output == response


def test_get_job_status_revoked_worker_disabled(
    client: TestClient, authorization_headers, user, attribute_matching_blocking_plugin
):
    worker_controller.pause_all_workers()

    dummy_body = _get_dummy_body(user.id, attribute_matching_blocking_plugin.id)

    request = client.post("/job/enrichAttribute", headers=authorization_headers, json=dummy_body)

    assert request.status_code == 200, "Job could not be created"

    sleep(1)

    job_id: int = request.json()["job_id"]

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=authorization_headers)

    assert cancel_resp.status_code == 200, "Job could not be created"

    worker_controller.reset_worker_queues()

    response: json = client.get(f"/job/{job_id}/status", headers=authorization_headers).json()

    expected_output = {"message": "The job was canceled before it could be processed", "status": "revoked"}

    assert expected_output == response


def test_remove_job(client: TestClient, authorization_headers, user, attribute_matching_blocking_plugin):
    worker_controller.pause_all_workers()

    dummy_body = _get_dummy_body(user.id, attribute_matching_blocking_plugin.id)

    client.post("/job/enrichAttribute", headers=authorization_headers, json=dummy_body)
    request = client.post("/job/enrichAttribute", headers=authorization_headers, json=dummy_body)

    assert request.status_code == 200, "Job could not be created"

    job_id: int = request.json()["job_id"]

    worker_controller.reset_worker_queues()

    cancel_resp = client.delete(f"/job/{job_id}/cancel", headers=authorization_headers)

    assert request.status_code == 200, "Job could not be created"

    expected_output = {"success": True}

    assert expected_output == cancel_resp.json()


def _get_dummy_body(user_id, attribute_matching_blocking_plugin_id):
    return {
        "user": {"user_id": user_id},
        "data": {"attribute_id": attribute_matching_blocking_plugin_id, "enrichment_plugins": ["Blocking Plugin"]},
    }
