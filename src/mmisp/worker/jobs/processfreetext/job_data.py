from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.attribute_type import AttributeType


class ProcessFreeTextData(BaseModel):
    """
    Represents the input data of the ProcessFreeTextJob
    """
    data: str


class ProcessFreeTextResponse(BaseModel):
    """
    Represents the response of the ProcessFreeTextJob
    """
    attributes: list[AttributeType]