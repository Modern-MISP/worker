from typing import Union

from pydantic import BaseModel, StringConstraints, UUID1, UUID3, UUID4, UUID5
from sqlmodel import Field
from typing_extensions import Annotated

from mmisp.worker.misp_dataclasses.misp_id import MispId


class EventTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event and a Tag.
    """

    id: MispId | None = None
    event_id: MispId | Union[UUID1, UUID3, UUID4, UUID5]
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None
