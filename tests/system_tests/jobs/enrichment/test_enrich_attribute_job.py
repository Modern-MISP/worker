from typing import Self, Type
from unittest import TestCase

from fastapi.testclient import TestClient
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from requests import Response

from mmisp.plugins.enrichment.data import EnrichAttributeResult

from ... import request_settings
from ...utility import check_status
from .dns_enrichment_utilities import DNSEnrichmentUtilities


class TestEnrichAttributeJob(TestCase):
    _event_id: int
    _attribute_id: int

    TEST_DOMAIN: str = "one.one.one.one"
    TEST_DOMAIN_IPS: list[str] = ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"]

    @classmethod
    def setUpClass(cls: Type["TestEnrichAttributeJob"], client: TestClient) -> None:
        test_event: tuple[int, list[int]] = DNSEnrichmentUtilities.prepare_enrichment_test([cls.TEST_DOMAIN])
        cls._event_id = test_event[0]
        cls._attribute_id = test_event[1][0]

        client.post(f"{request_settings.url}/worker/enrichment/enable", headers=request_settings.headers)

    def test_enrich_attribute_job(self: Self, client):
        create_job_url: str = f"{request_settings.url}/job/enrichAttribute"

        body: dict = {
            "user": {"user_id": 1},
            "data": {"attribute_id": self._attribute_id, "enrichment_plugins": [DNSResolverPlugin.PLUGIN_INFO.NAME]},
        }

        create_job_response: Response = client.post(create_job_url, json=body, headers=request_settings.headers)

        self.assertEqual(
            create_job_response.status_code, 200, f"Job could not be created. {create_job_response.json()}"
        )

        job_id: str = create_job_response.json()["job_id"]

        self.assertTrue(check_status(job_id, client), "Job failed.")

        get_job_result_url: str = f"{request_settings.url}/job/{job_id}/result"
        result_response: Response = client.get(f"{get_job_result_url}", headers=request_settings.headers)

        self.assertEqual(result_response.status_code, 200, f"Job result could not be fetched. {result_response.json()}")

        result: EnrichAttributeResult = EnrichAttributeResult.parse_obj(result_response.json())
        self.assertEqual(len(result.attributes), 1, "Unexpected Job result.")
        self.assertTrue(
            result.attributes[0].attribute.type == "ip-src" or result.attributes[0].attribute.type == "ip-dst"
        )
        self.assertEquals(result.attributes[0].attribute.category, "Network activity")
        self.assertEquals(result.attributes[0].attribute.object_id, 0)
        self.assertEqual(result.attributes[0].attribute.event_id, self._event_id)
        self.assertIn(result.attributes[0].attribute.value, self.TEST_DOMAIN_IPS)
