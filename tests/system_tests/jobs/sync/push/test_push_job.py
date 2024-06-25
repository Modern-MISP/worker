import json
import time
from typing import Self
from unittest import TestCase

import requests

data_full = {"user": {"user_id": 1}, "data": {"server_id": 1, "technique": "full"}}

data_incremental = {"user": {"user_id": 1}, "data": {"server_id": 1, "technique": "incremental"}}

url: str = "http://misp-03.mmisp.cert.kit.edu:5000"
headers: json = {"Authorization": "Bearer mispmisp"}

old_misp_url: str = "https://misp-02.mmisp.cert.kit.edu"
old_misp_headers: json = {
    "Authorization": "RlmznD5uUKg3MIaPYfzSK99WXVhcHJ1V692Ta7AE",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class TestPushJob(TestCase):
    def test_push_full(self: Self):
        create_response = requests.post(url + "/job/push", headers=headers, json=data_full).json()
        print(create_response["job_id"])
        job_id = self.check_status(create_response)
        response = requests.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertTrue(response["success"])

    def test_push_incremental(self: Self):
        requests.post(url + "/worker/push/enable", headers=headers).json()
        create_response = requests.post(url + "/job/push", headers=headers, json=data_incremental).json()
        print(create_response["job_id"])
        job_id = self.check_status(create_response)
        response = requests.get(url + f"/job/{job_id}/result", headers=headers).json()
        self.assertTrue(response["success"])

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
            request = requests.get(url + f"/job/{job_id}/status", headers=headers)
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
