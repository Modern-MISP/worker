import traceback

import pytest

from mmisp.db.models.event import Event
from mmisp.plugins.exceptions import PluginExecutionException
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin, PluginNotFound
from mmisp.worker.jobs.correlation.correlation_plugin_job import _correlation_plugin_job, correlation_plugin_job
from mmisp.worker.jobs.correlation.job_data import CorrelateValueResponse, CorrelationPluginJobData
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_info import CorrelationPluginInfo
from tests.plugins.correlation_plugins import correlation_test_plugin
from tests.plugins.correlation_plugins.correlation_test_plugin import CorrelationTestPlugin

from ..correlation.fixtures import CORRELATION_VALUE


@pytest.mark.asyncio
async def test_correlation_plugin_job(init_api_config, user, correlation_test_event, correlation_exclusion):
    event: Event = correlation_test_event

    # setup
    correlation_test_plugin.register(correlation_plugin_factory)

    is_registered: bool = correlation_plugin_factory.is_plugin_registered(CorrelationTestPlugin.PLUGIN_INFO.NAME)
    assert is_registered
    plugin_info: CorrelationPluginInfo = correlation_plugin_factory.get_plugin_info("CorrelationTestPlugin")
    assert CorrelationTestPlugin.PLUGIN_INFO == plugin_info

    # test
    user: UserData = UserData(user_id=user.id)
    data: CorrelationPluginJobData = CorrelationPluginJobData(
        correlation_plugin_name="CorrelationTestPlugin", value=CORRELATION_VALUE
    )
    try:
        result: CorrelateValueResponse = await _correlation_plugin_job(user, data)
    except Exception as e:
        print(e)
        traceback.print_exc()
        assert False
    expected: CorrelateValueResponse = CorrelateValueResponse(
        success=True,
        found_correlations=True,
        is_excluded_value=False,
        is_over_correlating_value=False,
        plugin_name="CorrelationTestPlugin",
        events=[event.uuid],
    )
    assert expected == result

    data.value = correlation_exclusion.value
    result_excluded: CorrelateValueResponse = await _correlation_plugin_job(user, data)
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
        await _correlation_plugin_job(user, data)
    except Exception as e:
        assert e is not None

    data.value = "just_exception"
    try:
        await _correlation_plugin_job(user, data)
    except Exception as e:
        assert e is not None

    data.value = "no_result"
    try:
        await _correlation_plugin_job(user, data)
    except PluginExecutionException as e:
        assert "The result of the plugin was None." == str(e)

    data.value = "one"
    result_one: CorrelateValueResponse = await _correlation_plugin_job(user, data)
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
        await _correlation_plugin_job(user, data)
    except NotAValidPlugin as e:
        assert "Plugin 'CorrelationTestPlugin' has incorrect constructor: Test." == str(e)


@pytest.mark.asyncio
async def test_not_registered():
    user: UserData = UserData(user_id=66)
    data: CorrelationPluginJobData = CorrelationPluginJobData(
        correlation_plugin_name="NotRegistered", value="correlation"
    )
    with pytest.raises(PluginNotFound) as e:
        correlation_plugin_job(user, data)
