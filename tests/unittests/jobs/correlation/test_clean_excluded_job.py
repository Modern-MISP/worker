import pytest

from mmisp.db.models.correlation import CorrelationExclusions
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.clean_excluded_correlations_job import _clean_excluded_correlations_job
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse


@pytest.mark.asyncio
async def test_run(db, correlating_value, user):
    exclusion: CorrelationExclusions = CorrelationExclusions(value=correlating_value.value, comment='Test')
    db.add(exclusion)
    await db.commit()
    await db.refresh(exclusion)

    user: UserData = UserData(user_id=user.id)
    result: DatabaseChangedResponse = await _clean_excluded_correlations_job(user)
    assert result.success
    assert result.database_changed
