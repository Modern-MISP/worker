import re

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


@celery_app.task
def processfreetext_job(user: UserData, data: ProcessFreeTextData) -> ProcessFreeTextResponse:
    liste: list = [AttributeType(types=["str"], default_type="str", value="str")]
    return ProcessFreeTextResponse(attributes=liste)


def __parse_attribute(attribute: str) -> AttributeType:
    pass


def __refang_input(input_str: str) -> str:
    data_str: str = re.sub(r'hxxp|hxtp|htxp|meow|h\[tt\]p', 'http', input_str, flags=re.IGNORECASE)
    data_str = re.sub(r'(\[\.\]|\[dot\]|\(dot\))', '.', data_str)
    data_str = re.sub(r'/\[hxxp:\/\/\]/', 'http://', data_str)
    data_str = re.sub(r'/[\@]|\[at\]', '@', data_str)
    data_str = re.sub(r'/\[:\]/', ':', data_str)
    data_str.removesuffix('.')
    if re.search(r'\[.\]', data_str):
        data_str = re.sub(r'\[(.)\]', lambda match: match.group(0)[1], data_str)
    return data_str


def __split_sentence(input_str: str) -> list[str]:
    words = re.split(r"[-,\s]+", string=input_str)
    for i in range(len(words)):
        words[i] = words[i].removesuffix('.')  # use .rstrip if multiple are changed
    return words


"""
    Test functions
"""
def test_split_sentence(input_str: str) -> list[str]:
    return __split_sentence(input_str)


def test_refang_input(input_str: str) -> str:
    return __refang_input(input_str)

