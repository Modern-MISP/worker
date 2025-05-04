import pytest

from mmisp.db.models.attribute import Attribute
from mmisp.tests.generators.model_generators.attribute_generator import generate_text_attribute
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.correlation_job import correlation_job
from mmisp.worker.jobs.correlation.job_data import CorrelationJobData, CorrelationResponse

user: UserData = UserData(user_id=66)


@pytest.mark.asyncio
async def test_excluded_value(db, attribute, correlation_exclusion):
    value = correlation_exclusion.value
    attribute.value = value
    await db.commit()

    test_data: CorrelationJobData = CorrelationJobData(attribute_id=attribute.id)
    result: CorrelationResponse = await correlation_job.run(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.events is None


@pytest.mark.asyncio
async def test_over_correlating_value(db, event, attribute):
    value = "overcorrelating"
    attribute.value = value
    await db.commit()

    # TODO: Adapt when correlation_threshold is readable/changable.
    correlation_threshold: int = 20
    attributes: list[Attribute] = []
    for i in range(correlation_threshold + 2):
        attribute: Attribute = generate_text_attribute(event.id, value)
        db.add(attribute)
        await db.commit()
        await db.refresh(attribute)
        attributes.append(attribute)

    test_data: CorrelationJobData = CorrelationJobData(attribute_id=attribute.id)
    result: CorrelationResponse = await correlation_job.run(user, test_data)

    assert result.success
    assert result.found_correlations
    assert not result.is_excluded_value
    assert result.is_over_correlating_value
    assert result.events is None

    for a in attributes:
        await db.delete(a)


@pytest.mark.asyncio
async def test_not_found_correlations(attribute, db):
    value = "notfound"
    attribute.value = value
    await db.commit()
    test_data: CorrelationJobData = CorrelationJobData(attribute_id=attribute.id)
    result: CorrelationResponse = await correlation_job.run(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.events is None
