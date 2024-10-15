from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from requests import Response

from mmisp.worker.controller import worker_controller
from mmisp.worker.jobs.enrichment.job_data import EnrichEventResult
from tests.system_tests import request_settings
from tests.system_tests.jobs.enrichment.dns_enrichment_utilities import DNSEnrichmentUtilities
from tests.system_tests.utility import check_status

TEST_DOMAINS: dict[str, list[str]] = {
    "one.one.one.one": ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"],
    "dns.google.com": ["8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844"],
}


def test_enrich_event_job(client, authorization_headers) -> None:
    test_event: tuple[int, list[int]] = DNSEnrichmentUtilities.prepare_enrichment_test(
        list(TEST_DOMAINS.keys()), client
    )
    _event_id: int = test_event[0]
    _attribute_ids: list[int] = []
    for attribute_id in test_event[1]:
        _attribute_ids.append(attribute_id)

    worker_controller.pause_all_workers()

    create_job_url: str = "/job/enrichEvent"

    body: dict = {
        "user": {"user_id": 1},
        "data": {"event_id": _event_id, "enrichment_plugins": [DNSResolverPlugin.PLUGIN_INFO.NAME]},
    }

    create_job_response: Response = client.post(create_job_url, json=body, headers=authorization_headers)
    worker_controller.reset_worker_queues()
    assert create_job_response.status_code == 200, f"Job could not be created. {create_job_response.json()}"

    job_id: str = create_job_response.json()["job_id"]
    assert check_status(client, authorization_headers, job_id), "Job failed."

    get_job_result_url: str = f"/job/{job_id}/result"
    result_response: Response = client.get(get_job_result_url, headers=authorization_headers)

    assert result_response.status_code == 200, f"Job result could not be fetched. {result_response.json()}"
    assert EnrichEventResult.parse_obj(result_response.json()).created_attributes == len(
        TEST_DOMAINS
    ), "Unexpected Job result."

    enriched_event_response: Response = client.get(
        f"{request_settings.old_misp_url}/events/view/{_event_id}", headers=request_settings.old_misp_headers
    )

    assert (
        enriched_event_response.status_code == 200
    ), f"Enriched Event could not be fetched. {enriched_event_response.json()}"
    enriched_event: dict = enriched_event_response.json()["Event"]

    assert (
        len(enriched_event["Attribute"]) == len(TEST_DOMAINS) * 2
    ), "Unexpected number of Attributes in enriched Event."

    for attribute_id in _attribute_ids:
        assert attribute_id in (int(result_attribute["id"]) for result_attribute in enriched_event["Attribute"])

    new_attributes: list[dict] = []
    for attribute in enriched_event["Attribute"]:
        if int(attribute["id"]) not in _attribute_ids:
            new_attributes.append(attribute)

    for attribute in new_attributes:
        is_attribute_value_correct: bool = False
        for ip_addresses in TEST_DOMAINS.values():
            if attribute["value"] in ip_addresses:
                is_attribute_value_correct = True
                break

        assert is_attribute_value_correct, "Unexpected Attribute in enriched Event."
        assert int(attribute["event_id"]) == _event_id, "Unexpected Event ID in enriched Attribute."
        assert attribute["type"] == "ip-src"
        assert attribute["category"] == "Network activity"
        assert int(attribute["object_id"]) == 0
