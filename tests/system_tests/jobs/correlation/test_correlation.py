from icecream import ic
from starlette.testclient import TestClient

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import CorrelateValueData, CorrelationPluginJobData
from tests.system_tests.utility import check_status


def test_correlate_value(client: TestClient, authorization_headers, site_admin_user, value="1.1.1.1") -> dict:
    body = {"user": UserData(user_id=site_admin_user.id).dict(), "data": CorrelateValueData(value=value).dict()}

    response = client.post("/job/correlateValue", json=body, headers=authorization_headers)

    assert response.status_code == 200, "Job could not be created"
    job_id = response.json()["job_id"]
    status_check = check_status(client, authorization_headers, job_id)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    ic(response)

    assert status_check, response

    #  response: dict = correlate_value("customers 042.js").dict()
    assert response["success"]
    assert response["found_correlations"]
    assert not response["is_excluded_value"]
    assert not response["is_over_correlating_value"]
    assert response["plugin_name"] is None
    assert response["events"] is not None

    return response


def test_plugin_list(client: TestClient, authorization_headers, site_admin_user):
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


def test_regenerate_occurrences(client: TestClient, authorization_headers, site_admin_user) -> bool:
    body = {"user": UserData(user_id=site_admin_user.id).dict()}
    response = client.post("/job/regenerateOccurrences", json=body, headers=authorization_headers)

    assert response.status_code == 200, "Job could not be created"
    job_id = response.json()["job_id"]
    assert check_status(client, authorization_headers, job_id)

    response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    assert response["success"]
    assert isinstance(response["database_changed"], bool)
    return response["database_changed"]


def test_top_correlations(client: TestClient, authorization_headers, site_admin_user):
    body = {"user": {"user_id": site_admin_user.id}}
    response = client.post("/job/topCorrelations", json=body, headers=authorization_headers)

    assert response.status_code == 200, "Job could not be created"
    job_id = response.json()["job_id"]
    assert check_status(client, authorization_headers, job_id)

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


def test_clean_excluded_job(client: TestClient, authorization_headers, site_admin_user) -> bool:
    body = {"user": UserData(user_id=site_admin_user.id).dict()}
    ic(body)
    response = client.post("/job/cleanExcluded", json=body, headers=authorization_headers)

    assert response.status_code == 200, response.text
    response_json = response.json()
    job_id = response_json["job_id"]
    assert check_status(client, authorization_headers, job_id)

    response_json = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    assert response_json["success"]
    assert isinstance(response_json["database_changed"], bool)
    return response_json["database_changed"]


def test_clean_excluded_job_twice(client: TestClient, authorization_headers, site_admin_user):
    test_clean_excluded_job(client, authorization_headers, site_admin_user)
    second: bool = test_clean_excluded_job(client, authorization_headers, site_admin_user)
    assert not second


def test_correlation_plugins(
    client: TestClient, authorization_headers, two_event_with_same_attribute_values, site_admin_user
):
    body = {
        "user": UserData(user_id=site_admin_user.id).dict(),
        "data": CorrelationPluginJobData(
            value=two_event_with_same_attribute_values[0][1].value, correlation_plugin_name="CorrelationTestPlugin"
        ).dict(),
    }
    response = client.post("/job/correlationPlugin", json=body, headers=authorization_headers)

    assert response.status_code == 200, "Job could not be created"
    job_id = response.json()["job_id"]
    status_check = check_status(client, authorization_headers, job_id)

    result_response = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()

    assert status_check, result_response.message
    assert result_response["success"]
    assert not result_response["is_excluded_value"]
    assert not result_response["is_over_correlating_value"]
    assert "CorrelationTestPlugin" == result_response["plugin_name"]

    uuid_set = set()
    uuid_set.add(two_event_with_same_attribute_values[0][0].uuid)
    uuid_set.add(two_event_with_same_attribute_values[1][0].uuid)
    assert set(result_response["events"]) == uuid_set

    comparison = test_correlate_value(client, authorization_headers, site_admin_user, "1.2.3.4")
    result_response["plugin_name"] = None
    assert result_response == comparison
