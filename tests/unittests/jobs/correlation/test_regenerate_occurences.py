import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.jobs.correlation.regenerate_occurrences_job import _regenerate_occurrences_job


@pytest.mark.asyncio
async def test_regenerate_occurences_job(user, correlating_value):
    # Test
    user: UserData = UserData(user_id=user.id)
    result: DatabaseChangedResponse = await _regenerate_occurrences_job(user)
    assert result.success
    assert result.database_changed
