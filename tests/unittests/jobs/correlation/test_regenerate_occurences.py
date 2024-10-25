from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import DatabaseChangedResponse
from mmisp.worker.jobs.correlation.regenerate_occurrences_job import regenerate_occurrences_job


def test_regenerate_occurences_job():
    # Test
    user: UserData = UserData(user_id=66)
    result: DatabaseChangedResponse = regenerate_occurrences_job.delay(user).get()
    assert result.success
    assert result.database_changed
