import time

data_full = {"user": {"user_id": 1}, "data": {"server_id": 1, "technique": "full"}}

data_incremental = {"user": {"user_id": 1}, "data": {"server_id": 1, "technique": "incremental"}}

url: str = "http://misp-03.mmisp.cert.kit.edu:5000"

old_misp_url: str = "https://misp-02.mmisp.cert.kit.edu"
old_misp_headers = {
    "Authorization": "RlmznD5uUKg3MIaPYfzSK99WXVhcHJ1V692Ta7AE",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def test_push_full(client, authorization_headers):
    assert False
    create_response = client.post(url + "/job/push", headers=authorization_headers, json=data_full).json()
    print(create_response["job_id"])
    job_id = check_status(client, authorization_headers, create_response)
    response = client.get(url + f"/job/{job_id}/result", headers=authorization_headers).json()
    assert response["success"]


def test_push_incremental(client, authorization_headers):
    assert False
    create_response = client.post(url + "/job/push", headers=authorization_headers, json=data_incremental).json()
    print(create_response["job_id"])
    job_id = check_status(client, authorization_headers, create_response)
    response = client.get(url + f"/job/{job_id}/result", headers=authorization_headers).json()
    assert response["success"]


def check_status(client, authorization_headers, response) -> str:
    job_id: str = response["job_id"]
    assert response["success"]
    ready: bool = False
    count: float = 0
    times: int = 0
    timer: float = 0.5
    while not ready:
        times += 1
        count += timer
        print(f"Time: {count}")
        request = client.get(url + f"/job/{job_id}/status", headers=authorization_headers)
        response = request.json()

        assert request.status_code == 200

        if response["status"] == "success":
            ready = True
            assert response["status"] == "success"
            assert response["message"] == "Job is finished"
        if response["status"] == "failed":
            assert False, response["message"]

        if times % 10 == 0 and times != 0:
            timer *= 2
        time.sleep(timer)
    print("Job is finished")
    return job_id
