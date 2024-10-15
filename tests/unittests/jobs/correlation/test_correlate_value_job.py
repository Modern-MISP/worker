from unittest.mock import patch

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value_job
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import CorrelateValueData, CorrelateValueResponse
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock

user: UserData = UserData(user_id=66)


@patch("mmisp.worker.jobs.correlation.utility.correlation_worker", autospec=True)
@patch("mmisp.worker.jobs.correlation.correlate_value_job.correlation_worker", autospec=True)
def test_correlate_value_job(correlation_worker_mock, utility_mock, correlation_exclusion_excluded):
    # Setup mock
    assert correlation_worker_mock.__class__.__name__ == correlation_worker.__class__.__name__

    correlation_worker_mock.misp_sql = MispSQLMock()
    correlation_worker_mock.misp_api = MispAPIMock()
    correlation_worker_mock.threshold = 20

    utility_mock.misp_sql = MispSQLMock()
    utility_mock.misp_api = MispAPIMock()

    # Test
    __test_excluded_value("excluded")
    __test_over_correlating_value("overcorrelating")
    __test_found_correlations("correlation")
    __test_not_found_correlations("notfound")


def __test_excluded_value(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


def __test_over_correlating_value(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job(user, test_data)

    assert result.success
    assert result.found_correlations
    assert not result.is_excluded_value
    assert result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


def __test_found_correlations(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is not None
    assert len(result.events) >= 0


def __test_not_found_correlations(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = correlate_value_job(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None
