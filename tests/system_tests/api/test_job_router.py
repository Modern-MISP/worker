from time import sleep
from unittest import TestCase

import requests

from pydantic import json
from tests.system_tests.request_settings import url, headers
from tests.system_tests.utility import check_status


class TestJobRouter(TestCase):
    _dummy_body: json = {
        "user": {
            "user_id": 3
        },
        "data": {
            "attribute_id": 272910,
            "enrichment_plugins": ["Blocking Plugin"]
        }
    }

    def test_get_job_status_success(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        data: json = {
            "user": {
                "user_id": 3
            },
            "data": {
                "attribute_id": 272910,
                "enrichment_plugins": []
            }
        }

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        request = requests.post(url + "/job/enrichAttribute", headers=headers, json=data)

        if request.status_code != 200:
            self.fail("Job could not be created")

        self.assertTrue(check_status(request.json()["job_id"]))

    def test_get_job_status_failed(self):
        assert requests.get(url + "/worker/sendEmail/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/sendEmail/enable", headers=headers)

        body: json = {
            "user": {
                "user_id": 1
            },
            "data": {
                "post_id": -69,
                "title": "test",
                "message": "test message",
                "receiver_ids": [
                    -69
                ]
            }
        }

        request = requests.post(url + "/job/postsEmail", json=body, headers=headers)
        if request.status_code != 200:
            self.fail("Job could not be created")

        job_id: int = request.json()["job_id"]

        sleep(2)

        response: json = requests.get(url + f"/job/{job_id}/status", headers=headers).json()

        expected_output = {'message': 'Job failed during execution', 'status': 'failed'}

        self.assertEqual(expected_output, response)

    def test_get_job_status_inProgress(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/enrichment/disable", headers=headers)

        request = requests.post(url + "/job/enrichAttribute", headers=headers, json=self._dummy_body)

        if request.status_code != 200:
            self.fail("Job could not be created")

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        sleep(4)

        job_id: int = request.json()["job_id"]

        response: json = requests.get(url + f"/job/{job_id}/status", headers=headers).json()

        expected_output = {'message': 'Job is currently being executed', 'status': 'inProgress'}

        # to ensure that the job is finished and the worker is free again for other tests
        self.assertTrue(check_status(job_id))

        self.assertEqual(expected_output, response)

    def test_get_job_status_queued(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/enrichment/disable", headers=headers)

        request = requests.post(url + "/job/enrichAttribute", headers=headers, json=self._dummy_body)

        if request.status_code != 200:
            self.fail("Job could not be created")

        job_id: int = request.json()["job_id"]

        response: json = requests.get(url + f"/job/{job_id}/status", headers=headers).json()

        expected_output = {'message': 'Job is currently enqueued', 'status': 'queued'}

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        # to ensure that the job is finished and the worker is free again for other tests
        self.assertTrue(check_status(job_id))

        self.assertEqual(expected_output, response)

    def test_get_job_status_revoked_worker_enabled(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        requests.post(url + "/job/enrichAttribute", headers=headers, json=self._dummy_body)
        request = requests.post(url + "/job/enrichAttribute", headers=headers, json=self._dummy_body)

        sleep(4)
        if request.status_code != 200:
            self.fail("Job could not be created")

        job_id: int = request.json()["job_id"]

        cancel_resp = requests.delete(url + f"/job/{job_id}/cancel", headers=headers)

        if cancel_resp.status_code != 200:
            self.fail("Job could not be canceled")

        sleep(4)

        response: json = requests.get(url + f"/job/{job_id}/status", headers=headers).json()

        expected_output = {'message': 'The job was canceled before it could be processed', 'status': 'revoked'}

        self.assertEqual(expected_output, response)

    def test_get_job_status_revoked_worker_disabled(self):

        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        # one worker has to be enabled to ensure that the job will be canceled
        requests.post(url + "/worker/sendEmail/enable", headers=headers)

        requests.post(url + "/worker/enrichment/disable", headers=headers)

        request = requests.post(url + "/job/enrichAttribute", headers=headers, json=self._dummy_body)

        if request.status_code != 200:
            self.fail("Job could not be created")

        sleep(1)

        job_id: int = request.json()["job_id"]

        cancel_resp = requests.delete(url + f"/job/{job_id}/cancel", headers=headers)

        if cancel_resp.status_code != 200:
            self.fail("Job could not be canceled")

        sleep(4)

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        sleep(4)

        response: json = requests.get(url + f"/job/{job_id}/status", headers=headers).json()

        expected_output = {'message': 'The job was canceled before it could be processed', 'status': 'revoked'}

        self.assertEqual(expected_output, response)

    def test_remove_job(self):
        assert requests.get(url + "/worker/enrichment/status", headers=headers).json()["jobs_queued"] == 0, \
            "Worker queue is not empty"

        requests.post(url + "/worker/enrichment/disable", headers=headers)

        requests.post(url + "/job/enrichAttribute", headers=headers, json=self._dummy_body)
        request = requests.post(url + "/job/enrichAttribute", headers=headers, json=self._dummy_body)

        if request.status_code != 200:
            self.fail("Job could not be created")

        job_id: int = request.json()["job_id"]

        requests.post(url + "/worker/enrichment/enable", headers=headers)

        sleep(5)

        cancel_resp = requests.delete(url + f"/job/{job_id}/cancel", headers=headers)

        if cancel_resp.status_code != 200:
            self.fail("Job could not be canceled")

        expected_output = {'success': True}

        self.assertEqual(expected_output, cancel_resp.json())
