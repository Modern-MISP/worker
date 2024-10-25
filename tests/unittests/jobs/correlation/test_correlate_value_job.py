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


def test_over_correlating_value():
    value = "overcorrelating"
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
