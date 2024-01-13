from src.api.job_router.input_data import UserData
from src.job.processfreetext_job.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from src.job.job import Job
from src.misp_dataclasses.attribute_type import AttributeType


class ProcessFreeTextJob(Job):

    def run(self,user: UserData, data: ProcessFreeTextData) -> ProcessFreeTextResponse:
        pass

    def __parse_attribute(self, attribute: str) -> AttributeType:
        pass

    def __refang_input(self, input):
        pass
