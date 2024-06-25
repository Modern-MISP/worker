from time import sleep

import requests

from tests.system_tests.request_settings import headers, url


def check_status(job_id) -> bool:
    ready: bool = False
    times: int = 0
    timer: float = 0.5
    while not ready:
        times += 1
        request = requests.get(url + f"/job/{job_id}/status", headers=headers)
        response = request.json()

        if request.status_code != 200:
            return False

        if response["status"] == "success":
            return True
        if response["status"] == "failed":
            return False

        if times % 10 == 0 and times != 0:
            timer *= 2
        sleep(timer)
