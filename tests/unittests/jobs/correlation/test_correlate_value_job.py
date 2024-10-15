from unittest.mock import patch

import pytest

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value_job
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import CorrelateValueData, CorrelateValueResponse
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock

user: UserData = UserData(user_id=66)


@pytest.mark.asyncio
@patch("mmisp.worker.jobs.correlation.utility.correlation_worker", autospec=True)
@patch("mmisp.worker.jobs.correlation.correlate_value_job.correlation_worker", autospec=True)
async def test_run(correlation_worker_mock, utility_mock):
    # Setup mock
    assert correlation_worker_mock.__class__.__name__ == correlation_worker.__class__.__name__

    correlation_worker_mock.misp_sql = MispSQLMock()
    correlation_worker_mock.misp_api = MispAPIMock()
    correlation_worker_mock.threshold = 20

    utility_mock.misp_sql = MispSQLMock()
    utility_mock.misp_api = MispAPIMock()

    # Test
    await __test_excluded_value("excluded")
    await __test_over_correlating_value("overcorrelating")
    await __test_found_correlations("correlation")
    await __test_not_found_correlations("notfound")


@pytest.mark.asyncio
async def __test_excluded_value(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = await correlate_value_job(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


@pytest.mark.asyncio
async def __test_over_correlating_value(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = await correlate_value_job(user, test_data)

    assert result.success
    assert result.found_correlations
    assert not result.is_excluded_value
    assert result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None


@pytest.mark.asyncio
async def __test_found_correlations(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = await correlate_value_job(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is not None
    assert len(result.events) >= 0


@pytest.mark.asyncio
async def __test_not_found_correlations(value: str):
    test_data: CorrelateValueData = CorrelateValueData(value=value)
    result: CorrelateValueResponse = await correlate_value_job(user, test_data)

    assert result.success
    assert not result.found_correlations
    assert not result.is_excluded_value
    assert not result.is_over_correlating_value
    assert result.plugin_name is None
    assert result.events is None
