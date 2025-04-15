import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound
from mmisp.worker.jobs.correlation.correlation_plugin_job import correlation_plugin_job
from mmisp.worker.jobs.correlation.job_data import CorrelationPluginJobData


@pytest.mark.asyncio
async def test_not_registered():
    user: UserData = UserData(user_id=66)
    data: CorrelationPluginJobData = CorrelationPluginJobData(
        correlation_plugin_name="NotRegistered", value="correlation"
    )
    with pytest.raises(PluginNotFound):
        await correlation_plugin_job.run(user, data)
