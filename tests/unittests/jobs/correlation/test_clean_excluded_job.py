import pytest

from mmisp.db.models.correlation import CorrelationExclusions
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.clean_excluded_correlations_job import clean_excluded_correlations_job
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.jobs.correlation.queue import queue


@pytest.mark.asyncio
async def test_run(db, correlating_value, user):
    exclusion: CorrelationExclusions = CorrelationExclusions(value=correlating_value.value, comment="Test")
    db.add(exclusion)
    await db.commit()
    await db.refresh(exclusion)

    user_data: UserData = UserData(user_id=user.id)
    async with queue:
        result: DatabaseChangedResponse = await clean_excluded_correlations_job.run(user_data)
    assert result.success
    assert result.database_changed

    await db.delete(exclusion)
    await db.commit()
