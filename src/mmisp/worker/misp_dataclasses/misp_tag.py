from typing import Union

from pydantic import BaseModel, StringConstraints, Field, model_validator, UUID4, UUID1, UUID3, UUID5
from pydantic_core import PydanticCustomError
from typing_extensions import Annotated

from mmisp.worker.misp_dataclasses.misp_id import MispId


class MispTag(BaseModel):
    """
    Encapsulates a MISP Tag attachable to Events and Attributes.
    """

    id: MispId
    name: Annotated[str, StringConstraints(min_length=1, max_length=255)] | None = None
    colour: Annotated[str, StringConstraints(regex="^#[0-9a-fA-F]{6}$")] | None = None
    exportable: bool | None = None
    org_id: MispId
    user_id: MispId
    hide_tag: bool | None = None
    numerical_value: int | None = None
    is_galaxy: bool | None = None
    is_custom_galaxy: bool | None = None
    local_only: bool | None = None
    inherited: Annotated[int, Field(le=2**31-1)]

    @model_validator(mode='after')
    def validate_tag(self):
        mandatory_alt1: list = [self.id]
        mandatory_alt2: list = [self.name, self.colour, self.org_id, self.user_id]

        if all(mandatory_alt1) or all(mandatory_alt2):
            return
        else:
            raise PydanticCustomError("Not enough values specified.",
                                      "Please provide an id of an already existing tag or a name, \
                                      colour, org-id and user-id so that a new tag can be created.")


class EventTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event and a Tag.
    """

    event_id: MispId | Union[UUID1, UUID3, UUID4, UUID5]
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None


class AttributeTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event-Attribute and a Tag.
    """

    attribute_id: MispId | Union[UUID1, UUID3, UUID4, UUID5] | None = None
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None

    def is_complete(self) -> bool:
        return self.attribute_id and self.tag_id
