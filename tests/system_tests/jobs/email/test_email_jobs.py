import time
from unittest import TestCase

import requests
from pydantic import json

from tests.system_tests.request_settings import url, headers
from tests.system_tests.utility import enable_worker, check_status


class TestEmailJobs(TestCase):

    def test_alert_email_job(self):

        if not enable_worker("sendEmail"):
            self.fail("Worker could not be enabled")

        body: json = {
            "user": {
                "user_id": 1
            },
            "data": {
                "event_id": 2,
                "old_publish": "1706736785",
                "receiver_ids": [
                    13
                ]
            }
        }

        request = requests.post(url + "/job/alertEmail", json=body, headers=headers)
        response = request.json()
        if not request.status_code == 200:
            self.fail("Job could not be created")

        if not check_status(response["job_id"]):
            self.fail("Job failed")

        self.assertEqual(True, True)

    def test_contact_email(self):

        if not enable_worker("sendEmail"):
            self.fail("Worker could not be enabled")

        body: json = {
            "user": {
                "user_id": 1
            },
            "data": {
                "event_id": 2,
                "message": "test message",
                "receiver_ids": [
                    13
                ]
            }
        }

        request = requests.post(url + "/job/contactEmail", json=body, headers=headers)
        response = request.json()
        if not request.status_code == 200:
            self.fail("Job could not be created")

        if not check_status(response["job_id"]):
            self.fail("Job failed")

        self.assertEqual(True, True)

    def test_posts_email(self):

        if not enable_worker("sendEmail"):
            self.fail("Worker could not be enabled")

        body: json = {
            "user": {
                "user_id": 1
            },
            "data": {
                "post_id": 1,
                "title": "test",
                "message": "test message",
                "receiver_ids": [
                    13
                ]
            }
        }

        request = requests.post(url + "/job/postsEmail", json=body, headers=headers)
        response = request.json()
        if not request.status_code == 200:
            self.fail("Job could not be created")

        if not check_status(response["job_id"]):
            self.fail("Job failed")

        self.assertEqual(True, True)
