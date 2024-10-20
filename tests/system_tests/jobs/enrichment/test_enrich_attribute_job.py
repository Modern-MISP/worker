from requests import Response
from starlette.testclient import TestClient

from mmisp.plugins.enrichment.data import EnrichAttributeResult
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from .dns_enrichment_utilities import DNSEnrichmentUtilities
from ...utility import check_status

TEST_DOMAIN: str = "one.one.one.one"
TEST_DOMAIN_IPS: list[str] = ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"]


def test_enrich_attribute_job(client: TestClient, authorization_headers) -> None:
    test_event: tuple[int, list[int]] = (
        DNSEnrichmentUtilities.prepare_enrichment_test([TEST_DOMAIN], client, authorization_headers))
    _event_id: int = test_event[0]
    _attribute_id: int = test_event[1][0]
    create_job_url: str = "/job/enrichAttribute"

    body: dict = {
        "user": {"user_id": 1},
        "data": {"attribute_id": _attribute_id, "enrichment_plugins": [DNSResolverPlugin.PLUGIN_INFO.NAME]},
    }

    create_job_response: Response = client.post(create_job_url, json=body, headers=authorization_headers)

    assert create_job_response.status_code == 200, f"Job could not be created. {create_job_response.json()}"

    job_id: str = create_job_response.json()["job_id"]

    assert check_status(client, authorization_headers, job_id), "Job failed."

    get_job_result_url: str = f"/job/{job_id}/result"
    result_response: Response = client.get(f"{get_job_result_url}", headers=authorization_headers)

    assert result_response.status_code == 200, f"Job result could not be fetched. {result_response.json()}"

    result: EnrichAttributeResult = EnrichAttributeResult.parse_obj(result_response.json())
    assert len(result.attributes) == 1, "Unexpected Job result."
    assert result.attributes[0].attribute.type == "ip-src" or result.attributes[0].attribute.type == "ip-dst"
    assert result.attributes[0].attribute.category == "Network activity"
    assert result.attributes[0].attribute.object_id == 0
    assert result.attributes[0].attribute.event_id == _event_id
    assert result.attributes[0].attribute.value in TEST_DOMAIN_IPS
