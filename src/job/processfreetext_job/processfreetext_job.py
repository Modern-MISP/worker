from src.misp_dataclasses import misp_attribute
from src.job.job import Job
from src.job.processfreetext_job.AttributeTypes.AttributeType import AttributeType


class ProcessFreeTextJob(Job):
    def run(self, job_id: int, user_id: int, data: str) -> list[misp_attribute]:
        pass

    def __parseAttribute(self, attribute: str) -> misp_attribute:
        pass

    def __refang_input(self, input):
        pass
