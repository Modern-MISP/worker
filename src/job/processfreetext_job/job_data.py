from pydantic import BaseModel

from src.misp_dataclasses.attribute_type import AttributeType


class ProcessFreeTextData(BaseModel):
    data: str


class ProcessFreeTextResponse(BaseModel):
    attributes: list[AttributeType]