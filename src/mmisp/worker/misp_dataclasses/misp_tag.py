from typing import Union, Dict, Any

from pydantic import BaseModel, StringConstraints, NonNegativeInt, model_validator, UUID1, UUID3, UUID4, UUID5, \
    model_serializer
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
        """
        Validates the tag by checking if the mandatory fields are present.

        :raises PydanticCustomError: If not all mandatory fields are present.
        :return: returns itself if all mandatory fields are present.
        :rtype: MispTag
        """
        mandatory_alt1: list = [self.id]
        mandatory_alt2: list = [self.name, self.colour, self.org_id, self.user_id]

        if not all(mandatory_alt1) and not all(mandatory_alt2):
            raise PydanticCustomError("Not enough values specified.",
                                      "Please provide an id of an already existing tag or a name, \
                                      colour, org-id and user-id so that a new tag can be created.")
        return self

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        """
        Serializes the MispTag to a dictionary used for json serialization.

        :return: returns the MispTag as a dictionary.
        :rtype: Dict[str, Any]
        """
        return {'id': self.id,
                'name': self.name,
                'colour': self.colour,
                'exportable': self.exportable,
                'org_id': self.org_id,
                'user_id': self.user_id,
                'hide_tag': self.hide_tag,
                'numerical_value': self.numerical_value,
                'is_galaxy': self.is_galaxy,
                'is_custom_galaxy': self.is_custom_galaxy,
                'local_only': self.local_only,
                'inherited': self.inherited,
                'attribute_count': self.attribute_count,
                'count': self.count,
                'favourite': self.favourite
                }


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
