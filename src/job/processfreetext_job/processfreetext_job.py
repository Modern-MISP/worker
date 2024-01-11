from pydantic import BaseModel
from src.job.processfreetext_job.job_data import ProcessFreeTextResponse
from src.misp_dataclasses import misp_attribute
from src.job.job import Job


class ProcessFreeTextData(BaseModel):
    data: str


class ProcessFreeTextJob(Job):
    def run(self, job_id: int, user_id: int, data: str) -> ProcessFreeTextResponse:
        pass

    def __parse_attribute(self, attribute: str) -> misp_attribute:
        pass

    def __refang_input(self, input):
        pass
