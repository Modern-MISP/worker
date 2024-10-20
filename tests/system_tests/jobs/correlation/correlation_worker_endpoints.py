from pydantic import json
from requests import Response
from starlette.testclient import TestClient


def test_change_threshold(client: TestClient, authorization_headers):
    body: json = {"user": {"user_id": 66}, "data": {"new_threshold": 25}}
    expected_output: json = {"saved": True, "valid_threshold": True, "new_threshold": 25}

    response: Response = client.put("/worker/correlation/changeThreshold", json=body, headers=authorization_headers)
    assert response.json() == expected_output

    body = {"user": {"user_id": 66}, "data": {"new_threshold": 20}}
    expected_output = {"saved": True, "valid_threshold": True, "new_threshold": 20}

    response = client.put("/worker/correlation/changeThreshold", json=body, headers=authorization_headers)
    assert response.json() == expected_output


def test_get_threshold(client: TestClient, authorization_headers):
    expected_output: json = {20}

    response: Response = client.get("/worker/correlation/threshold", headers=authorization_headers)
    assert response.json() == expected_output
