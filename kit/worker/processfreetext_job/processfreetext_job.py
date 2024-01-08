from kit.misp_dataclasses import misp_attribute
from kit.worker.job import Job
from kit.worker.processfreetext_job.AttributeTypes.AttributeType import AttributeType


class ProcessFreeTextJob(Job):
    def run(self, job_id: int, user_id: int, data: str) -> list[misp_attribute]:
        pass


    def __parseAttribute(self, attribute: str) -> misp_attribute:
        pass

    def __refangInput(self, input):
        pass