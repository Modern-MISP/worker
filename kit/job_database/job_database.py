from kit.job.job import Job


class JobDatabase:
    def get_job(self, job_id: int) -> Job:
        pass

    def update_job(self, job_id: int, job: Job) -> Job:
        pass

    def add_job(self, job: Job) -> int:
        pass
