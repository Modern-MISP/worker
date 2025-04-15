import pytest

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.correlation.job_data import TopCorrelationsResponse
from mmisp.worker.jobs.correlation.top_correlations_job import top_correlations_job


@pytest.mark.asyncio
async def test_run():
    user: UserData = UserData(user_id=66)
    result: TopCorrelationsResponse = await top_correlations_job.run(user)
    top_list: list[tuple[str, int]] = result.top_correlations
    correct_sorted: bool = all(top_list[i][1] >= top_list[i + 1][1] for i in range(len(top_list) - 1))
    assert result.success
    assert correct_sorted
