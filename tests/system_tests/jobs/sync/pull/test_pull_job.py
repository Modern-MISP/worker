import json
import time
from typing import Self
from unittest import TestCase

import pytest

data_full = {"user": {"user_id": 1}, "data": {"server_id": 1, "technique": "full"}}

data_incremental = {"user": {"user_id": 1}, "data": {"server_id": 1, "technique": "incremental"}}

data_pull_relevant_clusters = {"user": {"user_id": 1}, "data": {"server_id": 1, "technique": "pull_relevant_clusters"}}

url: str = "http://misp-03.mmisp.cert.kit.edu:5000"
headers: json = {"Authorization": "Bearer mispmisp"}

old_misp_url: str = "https://misp-02.mmisp.cert.kit.edu"
old_misp_headers: json = {
    "Authorization": "RlmznD5uUKg3MIaPYfzSK99WXVhcHJ1V692Ta7AE",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


@pytest.mark.usefixtures("client_class")
class TestPullJob(TestCase):
    def test_pull_full(self: Self):
        self.client.post(url + "/worker/pull/enable", headers=headers).json()
        create_response = self.client.post(url + "/job/pull", headers=headers, json=data_full).json()
        print(create_response["job_id"])
        job_id = self.check_status(create_response, client)
        response = self.client.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertIn("successes", response)
        self.assertIn("fails", response)
        self.assertIn("pulled_proposals", response)
        self.assertIn("pulled_sightings", response)
        self.assertIn("pulled_clusters", response)

    def test_pull_incremental(self: Self,):
        self.client.post(url + "/worker/pull/enable", headers=headers).json()
        create_response = self.client.post(url + "/job/pull", headers=headers, json=data_incremental).json()
        print(create_response["job_id"])
        job_id = self.check_status(create_response, self.client)
        response: json = self.client.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertIn("successes", response)
        self.assertIn("fails", response)
        self.assertIn("pulled_proposals", response)
        self.assertIn("pulled_sightings", response)
        self.assertIn("pulled_clusters", response)

    def test_pull_relevant_clusters(self: Self):
        self.client.post(url + "/worker/pull/enable", headers=headers).json()
        create_response = self.client.post(url + "/job/pull", headers=headers, json=data_pull_relevant_clusters).json()
        print(create_response["job_id"])
        job_id = self.check_status(create_response, client)
        response = self.client.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertIn("successes", response)
        self.assertIn("fails", response)
        self.assertIn("pulled_proposals", response)
        self.assertIn("pulled_sightings", response)
        self.assertIn("pulled_clusters", response)

    def check_status(self: Self, response) -> str:
        job_id: str = response["job_id"]
        self.assertTrue(response["success"])
        ready: bool = False
        count: float = 0
        times: int = 0
        timer: float = 0.5
        while not ready:
            times += 1
            count += timer
            print(f"Time: {count}")
            request = self.client.get(url + f"/job/{job_id}/status", headers=headers)
            response = request.json()

            self.assertEqual(request.status_code, 200)

            if response["status"] == "success":
                ready = True
                self.assertEqual(response["status"], "success")
                self.assertEqual(response["message"], "Job is finished")
            if response["status"] == "failed":
                self.fail(response["message"])

            if times % 10 == 0 and times != 0:
                timer *= 2
            time.sleep(timer)
        print("Job is finished")
        return job_id
