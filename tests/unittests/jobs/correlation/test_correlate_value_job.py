import asyncio

from mmisp.db.models.attribute import Attribute
from mmisp.tests.generators.model_generators.attribute_generator import generate_text_attribute
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value_job
from mmisp.worker.jobs.correlation.job_data import CorrelateValueData, CorrelateValueResponse

user: UserData = UserData(user_id=66)


def test_excluded_value(correlation_exclusion):
    value = correlation_exclusion.value
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert not result.found_correlations
    assert result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


def test_over_correlating_value(db, event):
    value = "overcorrelating"

    # TODO: Adapt when correlation_threshold is readable/changable.
    correlation_threshold: int = 20
    attributes: list[Attribute] = []
    for i in range(correlation_threshold + 2):
        attribute: Attribute = generate_text_attribute(event.id, value)
        asyncio.run(db.add(attribute))
        asyncio.run(db.commit())
        asyncio.run(db.refresh(attribute))
        attributes.append(attribute)

    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert result.found_correlations
    assert not result.is_excluded_value
    assert result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


def test_found_correlations():
    value = "correlation"
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is not None
    assert len(result.events) >= 0


def test_not_found_correlations(value: str):
    value = "notfound"
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None
