import unittest
from typing import Self
from unittest.mock import patch

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import TopCorrelationsResponse
from mmisp.worker.jobs.correlation.top_correlations_job import top_correlations_job
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestTopCorrelationsJob(unittest.TestCase):
    @patch("mmisp.worker.jobs.correlation.top_correlations_job.misp_sql", autospec=True)
    def test_run(self: Self, misp_sql_mock):
        misp_sql_mock = MispSQLMock()

        # Test
        user: UserData = UserData(user_id=66)
        result: TopCorrelationsResponse = top_correlations_job(user)
        top_list: list[tuple[str, int]] = result.top_correlations
        correct_sorted: bool = all(top_list[i][1] >= top_list[i + 1][1] for i in range(len(top_list) - 1))
        self.assertTrue(result.success)
        self.assertTrue(correct_sorted)
