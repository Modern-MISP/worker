import unittest
from typing import Any
from unittest.mock import patch

from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.jobs.correlation.regenerate_occurrences_job import regenerate_occurrences_job
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestTopCorrelationsJob(unittest.TestCase):

    @patch('mmisp.worker.jobs.correlation.correlate_value_job.correlation_worker', autospec=True)
    @patch('mmisp.worker.jobs.correlation.regenerate_occurrences_job.correlation_worker', autospec=True)
    def test_run(self, correlation_worker_mock, same_mock):
        # Setup mock
        assert correlation_worker_mock.__class__.__name__ == correlation_worker.__class__.__name__
        correlation_worker_mock.misp_sql = MispSQLMock()
        correlation_worker_mock.threshold = 20

        same_mock = correlation_worker_mock
        assert same_mock == correlation_worker_mock

        # Test
        result: DatabaseChangedResponse = regenerate_occurrences_job()
        self.assertTrue(result.success)
        self.assertTrue(result.database_changed)
        correlation_worker_mock.misp_sql.delete_over_correlating_value.assert_called_with("test_regenerate")
        correlation_worker_mock.misp_sql.add_over_correlating_value.assert_called_with("regenerate_correlation", 22)
