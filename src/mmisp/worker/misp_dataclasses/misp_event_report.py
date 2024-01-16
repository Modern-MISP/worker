from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MispEventReport(BaseModel):
    id: int
    uuid: UUID
    event_id: int
    name: str
    content: str
    distribution: str
    sharing_group_id: int
    timestamp: datetime
    deleted: bool
