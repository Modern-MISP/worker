import unittest
from unittest.mock import patch
from uuid import UUID

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.exceptions.plugin_exceptions import PluginExecutionException, NotAValidPlugin
from mmisp.worker.jobs.correlation.correlation_plugin_job import correlation_plugin_job
from mmisp.worker.jobs.correlation.job_data import CorrelationPluginJobData, CorrelateValueResponse
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from plugins.correlation_plugins.correlation_test_plugin import CorrelationTestPlugin, register
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


class TestCorrelationPluginJob(unittest.TestCase):

    @patch("mmisp.worker.jobs.correlation.utility.correlation_worker", autospec=True)
    @patch("mmisp.worker.jobs.correlation.correlation_plugin_job.correlation_worker")
    def test_run(self, worker_mock, utility_mock):
        # setup
        worker_mock.misp_sql = MispSQLMock()
        worker_mock.threshold = 20
        utility_mock.misp_sql = MispSQLMock()
        utility_mock.misp_api = MispAPIMock()

        plugin_info: CorrelationPluginInfo = correlation_plugin_factory.get_plugin_info("CorrelationTestPlugin")
        self.assertEqual(CorrelationTestPlugin.PLUGIN_INFO, plugin_info)
        is_registered: bool = correlation_plugin_factory.is_plugin_registered(CorrelationTestPlugin.PLUGIN_INFO.NAME)
        self.assertTrue(is_registered)

        # test
        user: UserData = UserData(user_id=66)
        data: CorrelationPluginJobData = CorrelationPluginJobData(correlation_plugin_name="CorrelationTestPlugin",
                                                                  value="correlation")
        result: CorrelateValueResponse = correlation_plugin_job(user, data)
        expected: CorrelateValueResponse = CorrelateValueResponse(success=True, found_correlations=True,
                                                                  is_excluded_value=False,
                                                                  is_over_correlating_value=False,
                                                                  plugin_name="CorrelationTestPlugin",
                                                                  events=[UUID('5019f511811a4dab800c80c92bc16d3d')])
        self.assertEqual(expected, result)

        data.value = "excluded"
        result_excluded: CorrelateValueResponse = correlation_plugin_job(user, data)
        expected_excluded: CorrelateValueResponse = CorrelateValueResponse(success=True, found_correlations=False,
                                                                        is_excluded_value=True,
                                                                         is_over_correlating_value=False,
                                                                         plugin_name="CorrelationTestPlugin",
                                                                          events=None)
        self.assertEqual(expected_excluded, result_excluded)

        data.value = "exception"
        try:
            correlation_plugin_job(user, data)
        except Exception as e:
            self.assertIsNotNone(e)

        data.value = "just_exception"
        try:
            correlation_plugin_job(user, data)
        except Exception as e:
            self.assertIsNotNone(e)

        data.value = "no_result"
        try:
            correlation_plugin_job(user, data)
        except PluginExecutionException as e:
            self.assertEqual("The result of the plugin was None.", str(e))

        data.value = "one"
        result_one: CorrelateValueResponse = correlation_plugin_job(user, data)
        expected_one: CorrelateValueResponse = CorrelateValueResponse(success=True, found_correlations=False,
                                                                     is_excluded_value=False,
                                                                     is_over_correlating_value=False,
                                                                     plugin_name="CorrelationTestPlugin",
                                                                     events=None)
        self.assertEqual(expected_one, result_one)

        data.value = "instructor_fail"
        try:
            correlation_plugin_job(user, data)
        except NotAValidPlugin as e:
            self.assertEqual("Plugin 'CorrelationTestPlugin' has incorrect constructor: Test.", str(e))

    def test_not_registered(self):
        user: UserData = UserData(user_id=66)
        data: CorrelationPluginJobData = CorrelationPluginJobData(correlation_plugin_name="NotRegistered",
                                                                  value="correlation")
        try:
            correlation_plugin_job(user, data)
            self.fail()
        except Exception as e:
            self.assertEqual("The plugin with the name NotRegistered was not found.", str(e))

