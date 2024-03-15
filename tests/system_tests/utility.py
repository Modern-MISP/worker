import time

import requests

from tests.system_tests.request_settings import url, headers


def enable_worker(worker_name: str) -> bool:
    if requests.post(url + f"/worker/{worker_name}/enable", headers=headers).status_code == 200:
        return True
    return False


def check_status(job_id) -> bool:
    ready: bool = False
    count: float = 0
    times: int = 0
    timer: float = 0.5
    while not ready:
        times += 1
        count += timer
        request = requests.get(url + f"/job/{job_id}/status", headers=headers)
        response = request.json()

        if not request.status_code == 200:
            return False

        if response["status"] == "success":
            return True
        if response["status"] == "failed":
            return False

        if times % 10 == 0 and times != 0:
            timer *= 2
        time.sleep(timer)
