from typing import Union

from pydantic import BaseModel, StringConstraints, NonNegativeInt, model_validator, UUID1, UUID3, UUID4, UUID5
from pydantic_core import PydanticCustomError
from sqlmodel import Field
from typing_extensions import Annotated

from mmisp.worker.misp_dataclasses.misp_id import MispId


class MispTag(BaseModel):
    """
    Encapsulates a MISP Tag attachable to Events and Attributes.
    """

    id: MispId | None = None
    name: Annotated[str, StringConstraints(min_length=1, max_length=255)] | None = None
    colour: Annotated[str, StringConstraints(pattern="^#[0-9a-fA-F]{6}$")] | None = None
    exportable: bool = True
    org_id: MispId | None = None
    user_id: MispId | None = None
    hide_tag: bool = False
    numerical_value: int | None = None
    is_galaxy: bool = True
    is_custom_galaxy: bool = True
    local_only: bool = True
    inherited: Annotated[int, Field(le=2 ** 31 - 1)] | None = None
    attribute_count: NonNegativeInt | None = None
    count: NonNegativeInt | None = None
    favourite: bool | None = None

    @model_validator(mode='after')
    def validate_tag(self):
        mandatory_alt1: list = [self.id]
        mandatory_alt2: list = [self.name, self.colour, self.org_id, self.user_id]

        if not all(mandatory_alt1) and not all(mandatory_alt2):
            raise PydanticCustomError("Not enough values specified.",
                                      "Please provide an id of an already existing tag or a name, \
                                      colour, org-id and user-id so that a new tag can be created.")


class EventTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event and a Tag.
    """

    id: MispId | None = None
    event_id: MispId | Union[UUID1, UUID3, UUID4, UUID5]
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None


class AttributeTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event-Attribute and a Tag.
    """

    id: MispId | None = None
    attribute_id: MispId | Union[UUID1, UUID3, UUID4, UUID5] | None = None
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None

    def is_complete(self) -> bool:
        return self.attribute_id and self.tag_id
