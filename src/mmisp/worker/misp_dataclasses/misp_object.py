from datetime import datetime
from typing import Self, List
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_object_attribute import MispObjectAttribute


class MispObject(BaseModel):
    id: int
    name: str
    meta_category: str
    description: str
    template_uuid: UUID
    template_version: int
    event_id: int
    uuid: UUID
    timestamp: datetime
    distribution: int
    sharing_group_id: int
    comment: str
    deleted: bool
    first_seen: datetime
    last_seen: datetime
    object_references: list["MispObject"]
    attributes: list[MispObjectAttribute]
