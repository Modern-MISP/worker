import time


def check_status(client, authorization_headers, response) -> str:
    job_id: str = response["job_id"]
    assert response["success"]
    ready: bool = False
    times: int = 0
    timer: float = 0.5
    while not ready:
        times += 1
        request = client.get(f"/job/{job_id}/status", headers=authorization_headers)
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
    return job_id


def test_correlate_value(client, authorization_headers) -> dict:
    body = {"user": {"user_id": 66}, "data": {"value": "1.1.1.1"}}

    response: dict = client.post("/job/correlateValue", json=body, headers=authorization_headers).json()
    job_id = check_status(client, authorization_headers, response)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()

    #  response: dict = correlate_value("customers 042.js").dict()
    assert response["success"]
    assert response["found_correlations"]
    assert not response["is_excluded_value"]
    assert not response["is_over_correlating_value"]
    assert response["plugin_name"] is None
    assert response["events"] is not None

    return response


def test_plugin_list(client, authorization_headers):
    response: list[dict] = client.get("/worker/correlation/plugins", headers=authorization_headers).json()
    test_plugin = response[0]
    expected_plugin = {
        "NAME": "CorrelationTestPlugin",
        "PLUGIN_TYPE": "correlation",
        "DESCRIPTION": "This is a plugin to test the correlation plugin integration.",
        "AUTHOR": "Tobias Gasteiger",
        "VERSION": "1.0",
        "CORRELATION_TYPE": "all",
    }
    assert test_plugin == expected_plugin


def test_regenerate_occurrences(client, authorization_headers) -> bool:
    body = {"user_id": 66}
    response: dict = client.post("/job/regenerateOccurrences", json=body, headers=authorization_headers).json()
    job_id: str = check_status(client, authorization_headers, response)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    assert response["success"]
    assert isinstance(response["database_changed"], bool)
    return response["database_changed"]


def test_top_correlations(client, authorization_headers):
    body = {"user_id": 66}
    response: dict = client.post("/job/topCorrelations", json=body, headers=authorization_headers).json()
    job_id: str = check_status(client, authorization_headers, response)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    result = response["top_correlations"]

    assert response["success"]
    assert isinstance(result, list)
    assert result is not None
    last: int = 1000000000000000000000000
    for res in result:
        assert 0 != res[1]
        assert last >= res[1]
        last = res[1]


def test_clean_excluded_job(client, authorization_headers) -> bool:
    body = {"user_id": 66}
    response: dict = client.post("/job/cleanExcluded", json=body, headers=authorization_headers).json()
    job_id: str = check_status(client, authorization_headers, response)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    assert response["success"]
    assert isinstance(response["database_changed"], bool)
    return response["database_changed"]


def test_clean_excluded_job_twice(client, authorization_headers):
    test_clean_excluded_job(client, authorization_headers)
    second: bool = test_clean_excluded_job(client, authorization_headers)
    assert not second


def test_correlation_plugins(client, authorization_headers):
    body = {
        "user": {"user_id": 66},
        "data": {"value": "1.1.1.1", "correlation_plugin_name": "CorrelationTestPlugin"},
    }
    response: dict = client.post("/job/correlationPlugin", json=body, headers=authorization_headers).json()
    job_id: str = check_status(client, authorization_headers, response)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    assert response["success"]
    # assert (response["found_correlations"])
    assert not response["is_excluded_value"]
    assert not response["is_over_correlating_value"]
    assert "CorrelationTestPlugin" == response["plugin_name"]
    assert response["events"] is not None

    comparison = test_correlate_value(client, authorization_headers)
    response["plugin_name"] = None
    assert response == comparison
