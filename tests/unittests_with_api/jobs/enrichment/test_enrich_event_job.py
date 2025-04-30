import pytest
import pytest_asyncio
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from sqlalchemy import delete

from mmisp.db.models.attribute import Attribute
from mmisp.tests.generators.model_generators.attribute_generator import generate_domain_attribute
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.enrichment.enrich_event_job import enrich_event_job, queue
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData

TEST_DOMAINS: dict[str, list[str]] = {
    "one.one.one.one": ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"],
    "dns.google.com": ["8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844"],
}


@pytest_asyncio.fixture
async def domain_attributes(db, event):
    attributes: list[Attribute] = []
    for domain in TEST_DOMAINS.keys():
        attribute: Attribute = generate_domain_attribute(event.id, domain)
        db.add(attribute)
        await db.commit()
        await db.refresh(attribute)
        attributes.append(attribute)

    await db.refresh(event)
    yield attributes

    for attribute in attributes:
        await db.delete(attribute)
    await db.commit()
    await db.refresh(event)


@pytest.mark.asyncio
async def test_enrich_event_job(db, init_api_config, domain_attributes, misp_api) -> None:
    event_id: int = domain_attributes[0].event_id
    attribute_ids: list[int] = [attribute.id for attribute in domain_attributes]

    print(f"test_enrich_event_job event1_uuid={domain_attributes[0].event.uuid}")
    print(f"test_enrich_event_job event1_uuid={domain_attributes[0].event_uuid}")
    print(f"test_enrich_event_job event2_uuid={domain_attributes[1].event.uuid}")
    print(f"test_enrich_event_job event2_uuid={domain_attributes[1].event_uuid}")
    async with queue:
        job_result = await enrich_event_job.run(
            UserData(user_id=1),
            EnrichEventData(event_id=event_id, enrichment_plugins=[DNSResolverPlugin.PLUGIN_INFO.NAME]),
        )
    assert job_result.created_attributes == len(TEST_DOMAINS), "Unexpected Job result."

    enriched_event = await misp_api.get_event(event_id)

    assert len(enriched_event.Attribute) == len(TEST_DOMAINS) * 2, "Unexpected number of Attributes in enriched Event."

    for attribute_id in attribute_ids:
        assert attribute_id in (int(result_attribute.id) for result_attribute in enriched_event.Attribute)

    new_attributes = []
    for attribute in enriched_event.Attribute:
        if int(attribute.id) not in attribute_ids:
            new_attributes.append(attribute)

    for attribute in new_attributes:
        is_attribute_value_correct: bool = False
        for ip_addresses in TEST_DOMAINS.values():
            if attribute.value in ip_addresses:
                is_attribute_value_correct = True
                break

        assert is_attribute_value_correct, "Unexpected Attribute in enriched Event."
        assert int(attribute.event_id) == event_id, "Unexpected Event ID in enriched Attribute."
        assert attribute.type == "ip-src"
        assert attribute.category == "Network activity"

    qry = delete(Attribute).filter(Attribute.event_id == event_id)
    await db.execute(qry)
