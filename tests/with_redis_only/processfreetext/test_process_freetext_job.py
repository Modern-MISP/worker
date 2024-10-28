from icecream import ic
from starlette.testclient import TestClient

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.controller import worker_controller
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData
from tests.system_tests.utility import check_status

data = {
    "user": UserData(user_id=0).dict(),
    "data": ProcessFreeTextData(data=
                                """Hallo Daniel, unsere Systeme wurden kürzlich von einem Virus infiltriert.
                                Die betroffene IP-Adresse lautet: 2001:0db8:85a3:0000:0000:8a2e:0370:7334.
                                Anbei findest du den Hash des Virus: 5d41402abc4b2a76b9719d911017c592.
                                Jegliche Interaktion mit der Bitcoin-Adresse 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa ist
                                untersagt. Bitte überprüfe deine Dateien und melde verdächtige Aktivitäten sofort.
                                Danke für deine Kooperation.""").dict(),
}

data2 = {
    "user": UserData(user_id=1).dict(),
    "data": ProcessFreeTextData(
        data="192.168.1.1:8080 a69c5d1f84205a46570bf12c7bf554d978c1d73f4cb2a08b3b8c7f5097dbb0bd "
             "1Emo4qE9HKfQQCV5Fqgt12j1C2quZbBy39 +1555-123-4567 test.example.com:8000 as123").dict(),
}


def test_processFreetext(client: TestClient, authorization_headers):
    create_response = client.post("/job/processFreeText", headers=authorization_headers, json=data).json()
    job_id = create_response["job_id"]
    expected = {
        "attributes": [
            {
                "types": ["ip-dst", "ip-src", "ip-src/ip-dst"],
                "default_type": "ip-dst",
                "value": "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            },
            {
                "types": ["md5", "imphash", "x509-fingerprint-md5", "ja3-fingerprint-md5"],
                "default_type": "md5",
                "value": "5d41402abc4b2a76b9719d911017c592",
            },
            {"types": ["btc"], "default_type": "btc", "value": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"},
        ]
    }
    assert check_status(client, authorization_headers, job_id), "Job failed."
    result = client.get(f"/job/{job_id}/result", headers=authorization_headers).json()
    ic("result is:", result)
    ic("expected is:", expected)
    assert result == expected


def test_scenario_processFreetext(client: TestClient, authorization_headers):
    worker_controller.pause_all_workers()

    create_response = client.post("/job/processFreeText", headers=authorization_headers, json=data2).json()
    job_id = create_response["job_id"]
    job_status = client.get(f"/job/{job_id}/status", headers=authorization_headers).json()
    status_waiting = {"status": "queued", "message": "Job is currently enqueued"}
    assert job_status == status_waiting

    worker_controller.reset_worker_queues()

    assert check_status(client, authorization_headers, job_id), "Job failed."
    expected = {
        "attributes": [
            {
                "types": ["ip-dst|port", "ip-src|port", "ip-src|port/ip-dst|port"],
                "default_type": "ip-dst|port",
                "value": "192.168.1.1|8080",
            },
            {
                "types": ["sha256", "authentihash", "sha512/256", "x509-fingerprint-sha256"],
                "default_type": "sha256",
                "value": "a69c5d1f84205a46570bf12c7bf554d978c1d73f4cb2a08b3b8c7f5097dbb0bd",
            },
            {"types": ["btc"], "default_type": "btc", "value": "1Emo4qE9HKfQQCV5Fqgt12j1C2quZbBy39"},
            {
                "types": ["hostname", "domain", "url", "filename"],
                "default_type": "hostname",
                "value": "test.example.com",
            },
            {"types": ["AS"], "default_type": "AS", "value": "AS123"},
        ]
    }
    assert client.get(f"/job/{job_id}/result", headers=authorization_headers).json() == expected
