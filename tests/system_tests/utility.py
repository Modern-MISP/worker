from time import sleep

from fastapi.testclient import TestClient
from icecream import ic


def check_status(client: TestClient, authorization_headers, job_id) -> bool:
    ready: bool = False
    counter: int = 0
    sleep_time: float = 2
    max_retries = 10

    while not ready:
        counter += 1
        request = client.get(f"/job/{job_id}/status", headers=authorization_headers)
        response = request.json()

        if request.status_code != 200:
            ic("check_status: API response code is not 200")
            print("check_status: API response code is not 200")
            return False

        if response["status"] == "success":
            ic("check_status: API response status success")
            print("check_status: API response status success")
            return True
        if response["status"] == "failed":
            print("API response status failed")
            ic("check_status: API response status failed")
            return False

        if counter > max_retries:
            print("check_status: counter reached max, break")
            ic("check_status: counter reached max, break")
            break
        sleep(sleep_time)
    return False
