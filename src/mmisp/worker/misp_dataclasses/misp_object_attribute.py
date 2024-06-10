from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MispObjectAttribute(BaseModel):
    """
    Encapsulates a MISP Object Attribute.
    """
    id: int
    type: str | None = None
    category: str | None = None
    to_ids: bool | None = None
    uuid: UUID | None = None
    event_id: int | None = None
    distribution: int | None = None
    timestamp: datetime | None = None
    comment: str | None = None
    sharing_group_id: int | None = None
    deleted: bool | None = None
    disable_correlation: bool | None = None
    object_id: int | None = None
    object_relation: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    value: str | None = None
