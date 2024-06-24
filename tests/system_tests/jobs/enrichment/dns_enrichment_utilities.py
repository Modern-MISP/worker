import requests
from requests import Response

from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from system_tests.jobs.enrichment.utilities import is_plugin_available
from system_tests.request_settings import old_misp_url, old_misp_headers


class DNSEnrichmentUtilities:
    @classmethod
    def prepare_enrichment_test(cls, attribute_domain_values: list[str]) -> tuple[int, list[int]]:
        assert is_plugin_available(DNSResolverPlugin.PLUGIN_INFO.NAME), "DNS Resolver Plugin not available."

        event_id: int = cls._create_event()
        attribute_ids: list[int] = []

        for value in attribute_domain_values:
            attribute_ids.append(DNSEnrichmentUtilities._create_domain_attribute(event_id, value))

        return event_id, attribute_ids

    @staticmethod
    def _create_event() -> int:
        event_body: dict = {
            "org_id": 0,
            "distribution": 0,
            "info": "Test Event for enrichment job.",
            "orgc_id": 0,
        }

        event_response: Response = requests.post(
            f"{old_misp_url}/events/add", headers=old_misp_headers, json=event_body
        )

        assert event_response.status_code == 200, f"Test Event could not be created. {event_response.json()}"

        return int(event_response.json()["Event"]["id"])

    @classmethod
    def _create_domain_attribute(cls, event_id: int, domain: str) -> int:
        attribute_body: dict = {
            "event_id": event_id,
            "object_id": 0,
            "category": "Network activity",
            "type": "domain",
            "value": domain,
        }

        attribute_response: Response = requests.post(
            f"{old_misp_url}/attributes/add/{event_id}", headers=old_misp_headers, json=attribute_body
        )

        assert (
            attribute_response.status_code == 200
        ), f"Test Attribute could not be created. {attribute_response.json()}"

        return int(attribute_response.json()["Attribute"]["id"])
