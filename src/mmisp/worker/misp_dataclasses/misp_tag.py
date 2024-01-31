from typing import Union

from pydantic import BaseModel, StringConstraints, Field, model_validator, UUID4, UUID1, UUID3, UUID5, NonNegativeInt
from pydantic_core import PydanticCustomError
from typing_extensions import Annotated

from mmisp.worker.misp_dataclasses.misp_id import MispId


class MispTag(BaseModel):
    """
    Encapsulates a MISP Tag attachable to Events and Attributes.
    """

    id: MispId | None = None # TODO added default none
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
        """
        print("id", self.id)
        print("name", self.name)
        print("colour", self.colour)
        print("org_id", self.org_id)
        print("user_id", self.user_id)
        print(not all(mandatory_alt1))
        print(all(mandatory_alt2))
        """
        if not all(mandatory_alt1) and not all(mandatory_alt2): # TODO Amadeus added second not to the last if and switched to and
            raise PydanticCustomError("Not enough values specified.",
                                      "Please provide an id of an already existing tag or a name, \
                                      colour, org-id and user-id so that a new tag can be created.")
        else:
            return self

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
