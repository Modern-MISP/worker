# worker management was changed completely. need to re-add functions to manage queues.

from starlette.testclient import TestClient


def get_worker_names(client: TestClient, authorization_headers: dict[str, str]):
    request = client.get("/worker/list_workers", headers=authorization_headers)
    list = request.json()
    return [worker["name"] for worker in list]


def test_get_worker_list_success(client: TestClient, authorization_headers: dict[str, str], user):
    request = client.get("/worker/list_workers", headers=authorization_headers)
    list = request.json()
    assert len(list) == 1, "List of workers is 0 should be 1"
    assert request.status_code == 200, "List of workers could not be retrieved"


def test_get_jobs_worker_success(client: TestClient, authorization_headers: dict[str, str], user):
    worker_names = get_worker_names(client, authorization_headers)
    for worker_name in worker_names:
        # maybe create a job for the worker and see if it is in the list
        request = client.get(f"/worker/jobs/{worker_name}", headers=authorization_headers)
        assert request.status_code == 200, "List of workers could not be retrieved"


def test_get_jobs_worker_failure(client: TestClient, authorization_headers: dict[str, str], user):
    request = client.get("/worker/jobs/abcdefg", headers=authorization_headers)
    assert request.status_code == 404, "Worker name found even though it should not exist"


def test_unpause_pause_worker_success(client: TestClient, authorization_headers: dict[str, str], user):
    worker_names = get_worker_names(client, authorization_headers)
    for worker_name in worker_names:
        request = client.post(f"/worker/pause/{worker_name}", headers=authorization_headers)
        assert request.status_code == 200, "Worker could not be paused"
    request = client.get("/worker/list_workers", headers=authorization_headers)
    list = request.json()
    for worker in list:
        assert len(worker["queues"]) == 0, "Worker is still active"

    for worker_name in worker_names:
        request = client.post(f"/worker/unpause/{worker_name}", headers=authorization_headers)
        assert request.status_code == 200, "Worker could not be unpaused"

    request = client.get("/worker/list_workers", headers=authorization_headers)
    list = request.json()
    for worker in list:
        assert len(worker["queues"]) != 0, "Worker is still active"


def test_unpause_pause_worker_failure(client: TestClient, authorization_headers: dict[str, str], user):
    request = client.post("/worker/pause/abcdefg", headers=authorization_headers)
    assert request.status_code == 404, "Worker name found even though it should not exist"


def test_list_all_queues_worker_success(client: TestClient, authorization_headers: dict[str, str], user):
    worker_names = get_worker_names(client, authorization_headers)
    for worker_name in worker_names:
        request = client.get(f"/worker/jobqueue/{worker_name}", headers=authorization_headers)
        assert request.status_code == 200, "List of workers could not be retrieved"


def test_list_all_queues_worker_failure(client: TestClient, authorization_headers: dict[str, str], user):
    request = client.get("/worker/jobqueue/abcdefg", headers=authorization_headers)
    assert request.status_code == 404, "Worker name found even though it should not exist"


def test_returning_jobs_success(client: TestClient, authorization_headers: dict[str, str], user):
    request = client.get("/worker/returningJobs", headers=authorization_headers)
    assert request.status_code == 200, "Returning jobs could not be retrieved"
