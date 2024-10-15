import unittest
from typing import Self
from unittest.mock import patch

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.jobs.correlation.regenerate_occurrences_job import regenerate_occurrences_job
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestRegenerateOccurrencesJob(unittest.TestCase):
    @patch("mmisp.worker.jobs.correlation.correlate_value_job.correlation_worker", autospec=True)
    @patch("mmisp.worker.jobs.correlation.regenerate_occurrences_job.correlation_worker", autospec=True)
    def test_run(self: Self, correlation_worker_mock):
        # Setup mock
        assert correlation_worker_mock.__class__.__name__ == correlation_worker.__class__.__name__
        correlation_worker_mock.misp_sql = MispSQLMock()
        correlation_worker_mock.threshold = 20

        same_mock = correlation_worker_mock
        assert same_mock == correlation_worker_mock

        # Test
        user: UserData = UserData(user_id=66)
        result: DatabaseChangedResponse = regenerate_occurrences_job(user)
        self.assertTrue(result.success)
        self.assertTrue(result.database_changed)
        correlation_worker_mock.misp_sql.delete_over_correlating_value.assert_called_with("not_there")
        correlation_worker_mock.misp_sql.add_over_correlating_value.assert_called_with("new_current", 22)
