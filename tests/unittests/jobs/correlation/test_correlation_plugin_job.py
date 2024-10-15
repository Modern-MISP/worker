from unittest.mock import patch
from uuid import UUID

from mmisp.plugins.exceptions import PluginExecutionException
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin
from mmisp.worker.jobs.correlation.correlation_plugin_job import correlation_plugin_job
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelationPluginJobData
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from plugins.correlation_plugins import correlation_test_plugin
from plugins.correlation_plugins.correlation_test_plugin import CorrelationTestPlugin
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock


@patch("mmisp.worker.jobs.correlation.utility.correlation_worker", autospec=True)
@patch("mmisp.worker.jobs.correlation.correlation_plugin_job.correlation_worker")
def test_correlation_plugin_job(worker_mock, utility_mock):
    # setup
    worker_mock.misp_sql = MispSQLMock()
    worker_mock.threshold = 20
    utility_mock.misp_sql = MispSQLMock()
    utility_mock.misp_api = MispAPIMock()

    correlation_test_plugin.register(correlation_plugin_factory)

    is_registered: bool = correlation_plugin_factory.is_plugin_registered(CorrelationTestPlugin.PLUGIN_INFO.NAME)
    assert is_registered
    plugin_info: CorrelationPluginInfo = correlation_plugin_factory.get_plugin_info("CorrelationTestPlugin")
    assert CorrelationTestPlugin.PLUGIN_INFO == plugin_info

    # test
    user: UserData = UserData(user_id=66)
    data: CorrelationPluginJobData = CorrelationPluginJobData(
        correlation_plugin_name="CorrelationTestPlugin", value="correlation"
    )
    result: CorrelateValueResponse = correlation_plugin_job(user, data)
    expected: CorrelateValueResponse = CorrelateValueResponse(
        success=True,
        found_correlations=True,
        is_excluded_value=False,
        is_over_correlating_value=False,
        plugin_name="CorrelationTestPlugin",
        events=[UUID("5019f511811a4dab800c80c92bc16d3d")],
    )
    assert expected == result

    data.value = "excluded"
    result_excluded: CorrelateValueResponse = correlation_plugin_job(user, data)
    expected_excluded: CorrelateValueResponse = CorrelateValueResponse(
        success=True,
        found_correlations=False,
        is_excluded_value=True,
        is_over_correlating_value=False,
        plugin_name="CorrelationTestPlugin",
        events=None,
    )
    assert expected_excluded == result_excluded

    data.value = "exception"
    try:
        correlation_plugin_job(user, data)
    except Exception as e:
        assert e is not None

    data.value = "just_exception"
    try:
        correlation_plugin_job(user, data)
    except Exception as e:
        assert e is not None

    data.value = "no_result"
    try:
        correlation_plugin_job(user, data)
    except PluginExecutionException as e:
        assert "The result of the plugin was None." == str(e)

    data.value = "one"
    result_one: CorrelateValueResponse = correlation_plugin_job(user, data)
    expected_one: CorrelateValueResponse = CorrelateValueResponse(
        success=True,
        found_correlations=False,
        is_excluded_value=False,
        is_over_correlating_value=False,
        plugin_name="CorrelationTestPlugin",
        events=None,
    )
    assert expected_one == result_one

    data.value = "instructor_fail"
    try:
        correlation_plugin_job(user, data)
    except NotAValidPlugin as e:
        assert "Plugin 'CorrelationTestPlugin' has incorrect constructor: Test." == str(e)


def test_not_registered():
    user: UserData = UserData(user_id=66)
    data: CorrelationPluginJobData = CorrelationPluginJobData(
        correlation_plugin_name="NotRegistered", value="correlation"
    )
    try:
        correlation_plugin_job(user, data)
        assert False
    except Exception as e:
        assert "The plugin with the name NotRegistered was not found." == str(e)
