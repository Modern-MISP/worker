from datetime import datetime
from typing import Self, List
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_object_attribute import MispObjectAttribute


class MispObject(BaseModel):
    """
    Encapsulates a MISP Object.
    """
    id: int
    name: str
    meta_category: str | None = None
    description: str | None = None
    template_uuid: UUID | None = None
    template_version: int | None = None
    event_id: int | None = None
    uuid: UUID | None = None
    timestamp: datetime | None = None
    distribution: int | None = None
    sharing_group_id: int | None = None
    comment: str | None = None
    deleted: bool | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    attributes: list[MispObjectAttribute] | None = None
