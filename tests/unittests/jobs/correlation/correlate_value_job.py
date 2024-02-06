import unittest
from unittest.mock import patch, Mock

from mmisp.worker.jobs.correlation.correlate_value_job import correlate_value, correlate_value_job
from mmisp.worker.jobs.correlation.correlation_worker import correlation_worker, CorrelationWorker
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelateValueData
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestCorrelateValueJob(unittest.TestCase):

    @patch('mmisp.worker.jobs.correlation.utility.correlation_worker', autospec=True)
    @patch('mmisp.worker.jobs.correlation.correlate_value_job.correlation_worker', autospec=True)
    def test_run(self, correlation_worker_mock, utility_mock):
        # Setup mock
        assert correlation_worker_mock.__class__.__name__ == correlation_worker.__class__.__name__

        correlation_worker_mock.misp_sql = MispSQLMock()
        correlation_worker_mock.misp_api = MispAPIMock()
        correlation_worker_mock.threshold = Mock()
        correlation_worker_mock.threshold.return_value = 20

        assert utility_mock.__class__.__name__ == correlation_worker.__class__.__name__

        utility_mock.misp_sql = MispSQLMock()
        utility_mock.misp_api = MispAPIMock()

        # Test
        self.__test_excluded_value("excluded")
        self.__test_over_correlating_value("overcorrelating")
        self.__test_found_correlations("correlation")
        self.__test_not_found_correlations("notfound")

    def __test_excluded_value(self, value: str):
        test_data: list[CorrelateValueData] = [CorrelateValueData(value=value)]
        result: CorrelateValueResponse = correlate_value_job(test_data[0])

        self.assertTrue(result.success)
        self.assertFalse(result.found_correlations)
        self.assertTrue(result.is_excluded_value)
        self.assertFalse(result.is_over_correlating_value)
        self.assertIsNone(result.plugin_name)
        self.assertIsNone(result.events)

    def __test_over_correlating_value(self, value: str):
        test_data: list[CorrelateValueData] = [CorrelateValueData(value=value)]
        result: CorrelateValueResponse = correlate_value_job(test_data[0])

        self.assertTrue(result.success)
        self.assertTrue(result.found_correlations)
        self.assertFalse(result.is_excluded_value)
        self.assertTrue(result.is_over_correlating_value)
        self.assertIsNone(result.plugin_name)
        self.assertIsNone(result.events)

    def __test_found_correlations(self, value: str):
        test_data: list[CorrelateValueData] = [CorrelateValueData(value=value)]
        result: CorrelateValueResponse = correlate_value_job(test_data[0])

        self.assertTrue(result.success)
        self.assertTrue(result.found_correlations)
        self.assertFalse(result.is_excluded_value)
        self.assertFalse(result.is_over_correlating_value)
        self.assertIsNone(result.plugin_name)
        self.assertIsNotNone(result.events)
        self.assertTrue(len(result.events) > 0)

    def __test_not_found_correlations(self, value: str):
        test_data: list[CorrelateValueData] = [CorrelateValueData(value=value)]
        result: CorrelateValueResponse = correlate_value_job(test_data[0])

        self.assertTrue(result.success)
        self.assertFalse(result.found_correlations)
        self.assertFalse(result.is_excluded_value)
        self.assertFalse(result.is_over_correlating_value)
        self.assertIsNone(result.plugin_name)
        self.assertIsNone(result.events)
