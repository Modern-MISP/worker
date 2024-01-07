from kit.misp_dataclasses import misp_attribute
from kit.worker.worker import Worker
from kit.worker.processfreetext_worker.AttributeTypes.AttributeType import AttributeType


class ProcessFreeTextWorker(Worker):
    def run(self, job_id: int, user_id: int, data: str) -> list[misp_attribute]:
        pass


    def __parseAttribute(self, attribute: str) -> misp_attribute:
        pass

    def __refangInput(self, input):
        pass