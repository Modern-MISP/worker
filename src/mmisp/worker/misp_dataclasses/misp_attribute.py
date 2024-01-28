from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_id import MispId
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, AttributeTagRelationship


class MispEventAttribute(BaseModel):
    """
    Encapsulates an MISP Event-Attribute.
    """

    id: MispId
    event_id: MispId
    object_id: MispId
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
