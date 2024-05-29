from typing import Union

from sqlmodel import Field
from typing_extensions import Annotated

from pydantic import BaseModel, UUID1, UUID3, UUID4, UUID5, StringConstraints

from mmisp.worker.misp_dataclasses.misp_id import MispId


class AttributeTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event-Attribute and a Tag.
    """

    id: MispId | None = None
    attribute_id: MispId | Union[UUID1, UUID3, UUID4, UUID5] | None = None
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None
