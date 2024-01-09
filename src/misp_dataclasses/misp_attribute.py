from uuid import UUID
from pydantic import BaseModel

from src.misp_dataclasses.misp_tag import MispTag, AttributeTagRelationship
# Needed to generate JSON Representation of dataclasses
from src.utilities.naming_utils import snake_to_camel_case


class MispEventAttribute(BaseModel):
    """
    Encapsulates an MISP Event-Attribute.
    """

    id: int
    event_id: int
    object_id: int
    object_relation: str
    category: str
    type: str
    to_ids: bool
    uuid: UUID
    timestamp: int
    distribution: int
    sharing_group_id: int
    comment: str
    deleted: bool
    disable_correlation: bool
    first_seen: int
    last_seen: int
    value: str
    event_uuid: UUID
    data: str
    tags: list[tuple[MispTag, AttributeTagRelationship]]
