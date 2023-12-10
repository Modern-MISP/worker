from kit.job.job import Job


class JobDatabase:
    def get_job(self, id: int) -> Job:
        pass

    def update_job(self, id: int, job: Job) -> Job:
        pass

    def add_job(self, job: Job) -> int:
        pass
