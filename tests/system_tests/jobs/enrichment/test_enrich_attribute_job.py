from unittest import TestCase

import requests
from requests import Response

from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from system_tests import request_settings
from system_tests.jobs.enrichment.dns_enrichment_utilities import DNSEnrichmentUtilities
from system_tests.utility import check_status


class TestEnrichAttributeJob(TestCase):
    _event_id: int
    _attribute_id: int

    TEST_DOMAIN: str = "one.one.one.one"
    TEST_DOMAIN_IPS: list[str] = ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"]

    @classmethod
    def setUpClass(cls):
        test_event: tuple[int, list[int]] = DNSEnrichmentUtilities.prepare_enrichment_test([cls.TEST_DOMAIN])
        cls._event_id = test_event[0]
        cls._attribute_id = test_event[1][0]

        requests.post(f"{request_settings.url}/worker/enrichment/enable", headers=request_settings.headers)

    def test_enrich_attribute_job(self):
        create_job_url: str = f"{request_settings.url}/job/enrichAttribute"

        body: dict = {
            "user": {"user_id": 1},
            "data": {"attribute_id": self._attribute_id, "enrichment_plugins": [DNSResolverPlugin.PLUGIN_INFO.NAME]},
        }

        create_job_response: Response = requests.post(create_job_url, json=body, headers=request_settings.headers)

        self.assertEqual(
            create_job_response.status_code, 200, f"Job could not be created. {create_job_response.json()}"
        )

        job_id: str = create_job_response.json()["job_id"]

        self.assertTrue(check_status(job_id), "Job failed.")

        get_job_result_url: str = f"{request_settings.url}/job/{job_id}/result"
        result_response: Response = requests.get(f"{get_job_result_url}", headers=request_settings.headers)

        self.assertEqual(result_response.status_code, 200, f"Job result could not be fetched. {result_response.json()}")

        result: EnrichAttributeResult = EnrichAttributeResult.model_validate(result_response.json())
        self.assertEqual(len(result.attributes), 1, "Unexpected Job result.")
        self.assertTrue(result.attributes[0].type == "ip-src" or result.attributes[0].type == "ip-dst")
        self.assertEquals(result.attributes[0].category, "Network activity")
        self.assertEquals(result.attributes[0].object_id, 0)
        self.assertEqual(result.attributes[0].event_id, self._event_id)
        self.assertIn(result.attributes[0].value, self.TEST_DOMAIN_IPS)
