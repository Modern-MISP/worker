import unittest
from unittest.mock import patch

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.correlation.clean_excluded_correlations_job import clean_excluded_correlations_job
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestCleanExcludedJob(unittest.TestCase):
    @patch("mmisp.worker.jobs.correlation.clean_excluded_correlations_job.correlation_worker", autospec=True)
    def test_run(self, correlation_worker_mock):
        # Setup mock
        assert correlation_worker_mock.__class__.__name__ == correlation_worker.__class__.__name__

        correlation_worker_mock.misp_sql = MispSQLMock()

        # Test
        user: UserData = UserData(user_id=66)
        result: DatabaseChangedResponse = clean_excluded_correlations_job(user)
        self.assertTrue(result.success)
        correlation_worker_mock.misp_sql.delete_correlations.assert_called_with("excluded")
        self.assertTrue(result.database_changed)
