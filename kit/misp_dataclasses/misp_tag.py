from pydantic import BaseModel

# Needed to generate JSON Representation of dataclasses
from kit.utilities.naming_utils import snake_to_camel_case


class MispTag(BaseModel):
    """
    Encapsulates a MISP Tag attachable to Events and Attributes.
    """

    id: int
    name: str
    colour: str
    exportable: bool
    org_id: int
    user_id: str
    hide_tag: bool
    numerical_value: int
    is_galaxy: bool
    is_custom_galaxy: bool
    local_only: bool
    inherited: int


class EventTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event and a Tag.
    """

    event_id: int
    tag_id: int
    local: int
    relationship_type: str


class AttributeTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event-Attribute and a Tag.
    """

    attribute_id: int
    tag_id: int
    local: int
    relationship_type: str
