import uuid
from typing import Self
from unittest import TestCase

from fastapi.testclient import TestClient
from pydantic import json

from tests.system_tests.request_settings import headers, old_misp_headers, old_misp_url
from tests.system_tests.utility import check_status


class TestEmailJobs(TestCase):
    # user_id of the user who should receive the email, make sure this user exists with an email address you can check
    _user_id: int = 52

    def _create_event(self: Self, client: TestClient) -> int:
        event_json: json = {
            "object_id": 0,
            "object_relation": None,
            "category": "Internal reference",
            "type": "hex",
            "to_ids": True,
            "uuid": str(uuid.uuid4()),
            "timestamp": 1706092974,
            "distribution": 0,
            "sharing_group_id": 0,
            "comment": None,
            "deleted": False,
            "disable_correlation": False,
            "first_seen": None,
            "last_seen": None,
            "value": "12345678900",
            "event_uuid": None,
            "data": None,
            "info": "edited info",
            "tags": [],
        }
        event_request = client.post(old_misp_url + "/events/add", headers=old_misp_headers, json=event_json)

        if event_request.status_code != 200:
            self.fail("Event could not be created")

        return event_request.json()["Event"]["id"]

    def test_alert_email_job(self: Self, client: TestClient):
        client.post("/worker/sendEmail/disable", headers=headers)

        body: json = {
            "user": {"user_id": 1},
            "data": {
                "event_id": self._create_event(client),
                "old_publish": "1706736785",
                "receiver_ids": [self._user_id],
            },
        }

        request = client.post("/job/alertEmail", json=body, headers=headers)
        if request.status_code != 200:
            self.fail("Job could not be created")

        client.post("/worker/sendEmail/enable", headers=headers)

        self.assertTrue(check_status(request.json()["job_id"], client))

    def test_contact_email(self: Self, client: TestClient):
        client.post("/worker/sendEmail/disable", headers=headers)

        body: json = {
            "user": {"user_id": self._user_id},
            "data": {
                "event_id": self._create_event(client),
                "message": "test message",
                "receiver_ids": [self._user_id],
            },
        }

        request = client.post("/job/contactEmail", json=body, headers=headers)
        if request.status_code != 200:
            self.fail("Job could not be created")

        client.post("/worker/sendEmail/enable", headers=headers)

        self.assertTrue(check_status(request.json()["job_id"], client))

    """
    Make sure the post_id exists
    """

    def test_posts_email(self: Self, client: TestClient):
        client.post("/worker/sendEmail/disable", headers=headers)

        body: json = {
            "user": {"user_id": 1},
            "data": {"post_id": 5, "title": "test", "message": "test message", "receiver_ids": [self._user_id]},
        }

        request = client.post("/job/postsEmail", json=body, headers=headers)
        if request.status_code != 200:
            self.fail("Job could not be created")

        client.post("/worker/sendEmail/enable", headers=headers)

        self.assertTrue(check_status(request.json()["job_id"], client))
