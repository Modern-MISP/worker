from starlette.testclient import TestClient

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller import worker_controller
from mmisp.worker.jobs.email.job_data import AlertEmailData, ContactEmailData, PostsEmailData
from tests.system_tests.utility import check_status


def test_alert_email_job(client: TestClient, authorization_headers, instance_owner_org_admin_user, event,
                         site_admin_user):
    worker_controller.pause_all_workers()

    body = {
        "user": UserData(user_id=site_admin_user.id).dict(),
        "data": AlertEmailData(event_id=event.id, old_publish="1706736785",
                               receiver_ids=[instance_owner_org_admin_user.id]).dict(),
    }

    request = client.post("/job/alertEmail", json=body, headers=authorization_headers)
    if request.status_code != 200:
        assert False, "Job could not be created"

    worker_controller.reset_worker_queues()

    assert check_status(client, authorization_headers, request.json()["job_id"])


def test_contact_email(client: TestClient, authorization_headers, instance_owner_org_admin_user, event,
                       site_admin_user):
    worker_controller.pause_all_workers()

    body = {
        "user": UserData(user_id=site_admin_user.id).dict(),
        "data": ContactEmailData(event_id=event.id, message="test message",
                                 receiver_ids=[instance_owner_org_admin_user.id]).dict(),
    }

    request = client.post("/job/contactEmail", json=body, headers=authorization_headers)
    if request.status_code != 200:
        assert False, "Job could not be created"

    worker_controller.reset_worker_queues()

    assert check_status(client, authorization_headers, request.json()["job_id"])


def test_posts_email(client: TestClient, authorization_headers, instance_owner_org_admin_user, post, site_admin_user):
    worker_controller.pause_all_workers()

    body = {
        "user": UserData(user_id=site_admin_user.id).dict(),
        "data": PostsEmailData(post_id=post.id, title="test", message="test message",
                               receiver_ids=[instance_owner_org_admin_user.id]).dict(),
    }

    request = client.post("/job/postsEmail", json=body, headers=authorization_headers)
    if request.status_code != 200:
        assert False, "Job could not be created"

    worker_controller.reset_worker_queues()

    assert check_status(client, authorization_headers, request.json()["job_id"])
