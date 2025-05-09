import pytest

from mmisp.plugins.exceptions import PluginNotFound
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.correlation_job import correlation_job
from mmisp.worker.jobs.correlation.job_data import CorrelationJobData


@pytest.mark.asyncio
async def test_not_registered(attribute):
    user: UserData = UserData(user_id=66)
    data: CorrelationJobData = CorrelationJobData(correlation_plugin_name="NotRegistered", attribute_id=attribute.id)
    with pytest.raises(PluginNotFound):
        await correlation_job.run(user, data)
