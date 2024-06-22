import re
from celery.utils.log import get_task_logger

from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery_client import celery_app
from mmisp.worker.jobs.processfreetext.attribute_types.type_validator import TypeValidator, IPTypeValidator, \
    EmailTypeValidator, DomainFilenameTypeValidator, PhonenumberTypeValidator, CVETypeValidator, ASTypeValidator, \
    BTCTypeValidator, HashTypeValidator
from mmisp.worker.jobs.processfreetext.job_data import ProcessFreeTextData, ProcessFreeTextResponse
from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType

JOB_NAME = "processfreetext_job"

validators: list[TypeValidator] = [IPTypeValidator(), EmailTypeValidator(), DomainFilenameTypeValidator(),
                                   PhonenumberTypeValidator(), CVETypeValidator(), ASTypeValidator(),
                                   BTCTypeValidator()]

logger = get_task_logger(__name__)


@celery_app.task
def processfreetext_job(user: UserData, data: ProcessFreeTextData) -> ProcessFreeTextResponse:
    """
    celery task that processes the given free text and returns a list of found attributes

    :param user: the user that requested the job
    :type user: UserData
    :param data: the data to process, containing the free text string
    :type data: ProcessFreeTextData
    :return: returns a list of found attributes
    :rtype: ProcessFreeTextData
    """
    found_attributes: list[AttributeType] = []
    word_list: list[str] = _split_text(data.data)
    for word in word_list:

        possible_attribute: AttributeType = _parse_attribute(word)
        if possible_attribute is not None:
            found_attributes.append(possible_attribute)
            logger.info(f"Found attribute: {possible_attribute}")
    logger.info("finished processing free text data")
    return ProcessFreeTextResponse(attributes=found_attributes)


def _parse_attribute(input_str: str) -> AttributeType | None:
    """
    Parses the given input string and returns the found attribute if it is valid, otherwise None

    :param input_str: input string to parse
    :type input_str: str
    :return: returns the found attribute if it is valid, otherwise None
    :rtype: AttributeType | None
    """
    possible_attribute = HashTypeValidator().validate(input_str)
    if possible_attribute is not None:
        return possible_attribute

    refanged_input = _refang_input(input_str)

    for extended_validator in validators:
        possible_attribute = extended_validator.validate(refanged_input)
        if possible_attribute is not None:
            return possible_attribute
    return None


def _refang_input(input_str: str) -> str:
    """
    Refangs the given input string and returns the refanged string

    :param input_str: input string to refang
    :type input_str: str
    :return: returns the refanged string
    :rtype: str
    """
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
    """
    Splits the given input string and returns a list of words

    :param input_str: input string to split
    :type input_str: str
    :return: returns a list of words, split by spaces, commas, and hyphens
    :rtype: list[str]
    """

    words = re.split(r"[-,\s]+", string=input_str)
    for i in range(len(words)):
        words[i] = words[i].removesuffix('.')
    return words
