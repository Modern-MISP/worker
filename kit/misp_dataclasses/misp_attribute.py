import json
from uuid import UUID
from pydantic import BaseModel

# Needed to generate JSON Representation of dataclasses
from kit.utilities.naming_utils import snake_to_camel_case


class EventAttribute(BaseModel):
    """
    Encapsulates an MISP Event-attribute.

    Contains all relevant information about an attribute.
    TODO: Nochmal auf Vollständigkeit überprüfen.
    TODO: Validierungsmethoden
    """

    event_id: int
    object_id: int
    object_relation: str
    category: str
    type: str
    value: str
    toIds: bool
    timestamp: int
    distribution: int
    sharing_group_id: int
    comment: str
    deleted: bool
    disable_correlation: bool
    first_seen: int
    last_seen: int

    id: int
    uuid: UUID
    event_uuid: UUID
    data: str

    def to_json(self) -> str:
        pass
