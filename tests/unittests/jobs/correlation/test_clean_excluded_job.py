import unittest
from typing import Self
from unittest.mock import patch

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.clean_excluded_correlations_job import clean_excluded_correlations_job
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.misp_database import misp_sql
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestCleanExcludedJob(unittest.TestCase):
    @patch("mmisp.worker.jobs.correlation.clean_excluded_correlations_job.misp_sql", autospec=True)
    def test_run(self: Self, misp_sql_mock):
        # Setup mock
        assert misp_sql_mock == misp_sql

        misp_sql_mock = MispSQLMock()

        # Test
        user: UserData = UserData(user_id=66)
        result: DatabaseChangedResponse = clean_excluded_correlations_job(user)
        self.assertTrue(result.success)
        misp_sql_mock.delete_correlations.assert_called_with("excluded")
        self.assertTrue(result.database_changed)
