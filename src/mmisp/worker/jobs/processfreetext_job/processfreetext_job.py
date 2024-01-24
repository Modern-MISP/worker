from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.job.processfreetext_job.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.job.job import Job
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class ProcessFreeTextJob(Job):

    def run(self,user: UserData, data: ProcessFreeTextData) -> ProcessFreeTextResponse:
        pass

    def __parse_attribute(self, attribute: str) -> AttributeType:
        pass

    def __refang_input(self, input):
        pass
