from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value_job
from mmisp.worker.jobs.correlation.job_data import CorrelateValueData, CorrelateValueResponse

user: UserData = UserData(user_id=66)


def test_correlate_value_job(correlation_exclusion):
    __test_excluded_value(correlation_exclusion.value)
    __test_over_correlating_value("overcorrelating")
    __test_found_correlations("correlation")
    __test_not_found_correlations("notfound")


def __test_excluded_value(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert not result.found_correlations
    assert result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


def __test_over_correlating_value(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert result.found_correlations
    assert not result.is_excluded_value
    assert result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


def __test_found_correlations(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is not None
    assert len(result.events) >= 0


def __test_not_found_correlations(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job.delay(user, test_data).get()

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None
