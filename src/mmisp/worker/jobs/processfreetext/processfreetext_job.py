import re

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_app.celery_app import celery_app
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import TypeValidator, IPTypeValidator, \
    EmailTypeValidator, DomainFilenameTypeValidator, PhonenumberTypeValidator, CVETypeValidator, ASTypeValidator, \
    BTCTypeValidator, HashTypeValidator
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.misp_dataclasses.attribute_type import AttributeType

extended_validators: list[TypeValidator] = [IPTypeValidator(), EmailTypeValidator(), DomainFilenameTypeValidator(),
                                            PhonenumberTypeValidator(), CVETypeValidator(), ASTypeValidator(),
                                            BTCTypeValidator()]

"""
ask link/url
add logger to worker
"""


@celery_app.task
def processfreetext_job(user: UserData, data: ProcessFreeTextData) -> ProcessFreeTextResponse:
    found_attributes: list[AttributeType] = []
    word_list: list[str] = _split_text(data.data)

    for word in word_list:
        possible_attribute: AttributeType = __parse_attribute(word)
        if possible_attribute is not None:
            found_attributes.append(possible_attribute)
    return ProcessFreeTextResponse(attributes=found_attributes)


def __parse_attribute(input_str: str) -> AttributeType:
    possible_attribute = HashTypeValidator.validate(input_str)
    if possible_attribute is not None:
        return possible_attribute

    refanged_input = _refang_input(input_str)

    for extended_validator in extended_validators:
        possible_attribute = extended_validator.validate(refanged_input)
        if possible_attribute is not None:
            return possible_attribute
    return None


def _refang_input(input_str: str) -> str:
    data_str: str = re.sub(r'hxxp|hxtp|htxp|meow|h\[tt\]p', 'http', input_str, flags=re.IGNORECASE)
    data_str = re.sub(r'(\[\.\]|\[dot\]|\(dot\))', '.', data_str)
    data_str = re.sub(r'/\[hxxp:\/\/\]/', 'http://', data_str)
    data_str = re.sub(r'/[\@]|\[at\]', '@', data_str)
    data_str = re.sub(r'/\[:\]/', ':', data_str)
    data_str.removesuffix('.')
    if re.search(r'\[.\]', data_str):
        data_str = re.sub(r'\[(.)\]', lambda match: match.group(0)[1], data_str)
    return data_str


def _split_text(input_str: str) -> list[str]:
    words = re.split(r"[-,\s]+", string=input_str)
    for i in range(len(words)):
        words[i] = words[i].removesuffix('.')  # use .rstrip if multiple are changed
    return words


"""
    Test functions
"""
