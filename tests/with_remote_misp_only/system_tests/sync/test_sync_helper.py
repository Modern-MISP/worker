from asyncio import sleep

from mmisp.worker.api.response_schemas import CreateJobResponse, JobStatusEnum, JobStatusResponse


async def check_status(client, response: CreateJobResponse, authorization_headers) -> str:
    job_id: str = response.job_id
    assert response.success
    ready: bool = False
    count: float = 0
    times: int = 0
    timer: float = 0.5
    while not ready:
        request = client.get(f"/job/{job_id}/status", headers=authorization_headers)
        response: JobStatusResponse = JobStatusResponse.model_validate(request.json())

        assert request.status_code == 200

        if response.status == JobStatusEnum.SUCCESS:
            assert response.message == "Job is finished"
            return job_id
        assert response.status != JobStatusEnum.FAILED, response.message

        times += 1
        count += timer
        if times % 10 == 0 and times != 0:
            timer *= 2
        await sleep(timer)
    return job_id
