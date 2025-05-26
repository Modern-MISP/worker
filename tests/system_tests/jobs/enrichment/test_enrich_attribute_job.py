import pytest
import pytest_asyncio
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from requests import Response
from starlette.testclient import TestClient

from mmisp.db.models.attribute import Attribute
from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute
from mmisp.tests.generators.model_generators.attribute_generator import generate_domain_attribute
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData

from ...utility import check_status

TEST_DOMAIN: str = "one.one.one.one"
TEST_DOMAIN_IPS: list[str] = ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"]


@pytest_asyncio.fixture
async def domain_attribute(db, event) -> Attribute:
    attribute: Attribute = generate_domain_attribute(event.id, TEST_DOMAIN)
    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)
    await db.refresh(event)

    yield attribute

    await db.delete(attribute)
    await db.commit()


@pytest.mark.asyncio
async def test_enrich_attribute_job(
    client: TestClient, init_api_config, authorization_headers, domain_attribute
) -> None:
    event_id: int = domain_attribute.event_id

    create_job_url: str = "/job/enrichAttribute"
    body: dict = {
        "user": UserData(user_id=1).dict(),
        "data": EnrichAttributeData(
            attribute_id=domain_attribute.id, enrichment_plugins=[DNSResolverPlugin.PLUGIN_INFO.NAME]
        ).dict(),
    }
    create_job_response: Response = client.post(create_job_url, json=body, headers=authorization_headers)
    assert create_job_response.status_code == 200, f"Job could not be created. {create_job_response.json()}"

    job_id: str = create_job_response.json()["job_id"]
    assert check_status(client, authorization_headers, job_id), "Job failed."

    get_job_result_url: str = f"/job/{job_id}/result"
    result_response: Response = client.get(f"{get_job_result_url}", headers=authorization_headers)
    assert result_response.status_code == 200, f"Job result could not be fetched. {result_response.json()}"

    result: EnrichAttributeResult = EnrichAttributeResult.model_validate(result_response.json())
    assert len(result.attributes) == 1, "Unexpected Job result."

    attribute: NewAttribute = result.attributes[0]
    assert attribute.attribute.type == "ip-src" or attribute.attribute.type == "ip-dst"
    assert attribute.attribute.category == "Network activity"
    assert attribute.attribute.object_id == 0
    assert attribute.attribute.event_id == event_id
    assert attribute.attribute.value in TEST_DOMAIN_IPS
