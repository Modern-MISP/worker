from datetime import datetime
from typing import Self, List
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_object_attribute import MispObjectAttribute


class MispObject(BaseModel):
    id: int
    name: str
    meta_category: str | None = None
    description: str
    template_uuid: UUID
    template_version: int
    event_id: int
    uuid: UUID
    timestamp: datetime | None = None
    distribution: int
    sharing_group_id: int
    comment: str
    deleted: bool
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    #object_references: list["MispObject"] TODO löschen falls nimand es braucht
    attributes: list[MispObjectAttribute] | None = None
