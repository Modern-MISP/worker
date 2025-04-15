import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.jobs.correlation.regenerate_occurrences_job import regenerate_occurrences_job


@pytest.mark.asyncio
async def test_regenerate_occurrences_job(user, correlating_value):
    # Test
    user: UserData = UserData(user_id=user.id)
    result: DatabaseChangedResponse = await regenerate_occurrences_job.run(user)
    assert result.success
    assert result.database_changed
