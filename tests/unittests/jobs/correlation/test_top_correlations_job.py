import unittest
from unittest.mock import patch

from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker
from mmisp.worker.jobs.correlation.job_data import TopCorrelationsResponse
from mmisp.worker.jobs.correlation.top_correlations_job import top_correlations_job
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestTopCorrelationsJob(unittest.TestCase):

    @patch('mmisp.worker.jobs.correlation.top_correlations_job.correlation_worker', autospec=True)
    def test_run(self, correlation_worker_mock):
        # Setup mock
        assert correlation_worker_mock.__class__.__name__ == correlation_worker.__class__.__name__

        correlation_worker_mock.misp_sql = MispSQLMock()

        # Test
        result: TopCorrelationsResponse = top_correlations_job()
        top_list: list[tuple[str, int]] = result.top_correlations
        correct_sorted: bool = all(top_list[i][1] >= top_list[i+1][1] for i in range(len(top_list)-1))
        self.assertTrue(result.success)
        self.assertTrue(correct_sorted)
