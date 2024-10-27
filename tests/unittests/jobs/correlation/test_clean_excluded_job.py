import asyncio

from mmisp.db.models.correlation import CorrelationExclusions
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.clean_excluded_correlations_job import clean_excluded_correlations_job
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse


def test_run(db, correlating_value):
    exclusion: CorrelationExclusions = CorrelationExclusions(value=correlating_value.value, comment='Test')
    db.add(exclusion)
    asyncio.run(db.commit())
    asyncio.run(db.refresh(exclusion))

    user: UserData = UserData(user_id=66)
    result: DatabaseChangedResponse = clean_excluded_correlations_job.delay(user).get()
    assert result.success
    assert result.database_changed
