import json

import requests
from unittest import TestCase

from tests.system_tests.request_settings import url, headers

from tests.system_tests.utility import check_status

data = {
    "user": {"user_id": 0},
    "data": {
        "data": """Hallo Daniel, unsere Systeme wurden kürzlich von einem Virus infiltriert. Die betroffene IP-Adresse
         lautet: 2001:0db8:85a3:0000:0000:8a2e:0370:7334. Anbei findest du den Hash des Virus: 5d41402abc4b2a76b9719d911017c592. Jegliche Interaktion mit der Bitcoin-Adresse
          1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa ist untersagt. Bitte überprüfe deine Dateien und melde verdächtige Aktivitäten sofort.
          Danke für deine Kooperation."""
    }
}

data2: json = {
    "user": {
        "user_id": 1
    },
    "data": {
        "data": "192.168.1.1:8080 a69c5d1f84205a46570bf12c7bf554d978c1d73f4cb2a08b3b8c7f5097dbb0bd 1Emo4qE9HKfQQCV5Fqgt12j1C2quZbBy39 +1555-123-4567 test.example.com:8000 as123"
    }
}


class TestEmailJobs(TestCase):

    def test_scenario_processFreetext(self):
        requests.post(url + "/worker/processFreeText/enable", headers=headers).json()
        create_response = requests.post(url + "/job/processFreeText", headers=headers, json=data).json()
        job_id = create_response["job_id"]
        expected = {'attributes': [{'types': ['ip-dst', 'ip-src', 'ip-src/ip-dst'], 'default_type': 'ip-dst',
                                    'value': '2001:0db8:85a3:0000:0000:8a2e:0370:7334'},
                                   {'types': ['md5', 'imphash', 'x509-fingerprint-md5', 'ja3-fingerprint-md5'],
                                    'default_type': 'md5', 'value': '5d41402abc4b2a76b9719d911017c592'},
                                   {'types': ['btc'], 'default_type': 'btc',
                                    'value': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'}]}

        self.assertEqual(requests.get(url + f"/job/{job_id}/result", headers=headers).json(), expected)

    def test_processFreetext(self):
        requests.post(url + "/worker/processFreeText/enable", headers=headers).json()
        create_response = requests.post(url + "/job/processFreeText", headers=headers, json=data2).json()
        job_id = create_response["job_id"]
        expected = {'attributes': [
            {'types': ['ip-dst|port', 'ip-src|port', 'ip-src|port/ip-dst|port'], 'default_type': 'ip-dst|port',
             'value': '192.168.1.1|8080'},
            {'types': ['sha256', 'authentihash', 'sha512/256', 'x509-fingerprint-sha256'], 'default_type': 'sha256',
             'value': 'a69c5d1f84205a46570bf12c7bf554d978c1d73f4cb2a08b3b8c7f5097dbb0bd'},
            {'types': ['btc'], 'default_type': 'btc', 'value': '1Emo4qE9HKfQQCV5Fqgt12j1C2quZbBy39'},
            {'types': ['hostname', 'domain', 'url', 'filename'], 'default_type': 'hostname',
             'value': 'test.example.com'}, {'types': ['AS'], 'default_type': 'AS', 'value': 'AS123'}]}
        job_status = requests.get(url + f"/job/{job_id}/status", headers=headers).json()
        self.assertEqual(job_status, {'status': 'inProgress', 'message': 'Job is currently beeing executed'})
        check_status(job_id)
        self.assertEqual(requests.get(url + f"/job/{job_id}/result", headers=headers).json(), expected)
