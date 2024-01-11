from pydantic import BaseModel

from src.misp_dataclasses.misp_attribute import MispEventAttribute


class ProcessFreeTextResponse(BaseModel):
    attributes: list[MispEventAttribute]