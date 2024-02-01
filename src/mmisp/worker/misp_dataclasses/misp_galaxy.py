
from uuid import UUID

from pydantic import BaseModel


class MispGalaxy(BaseModel):
    id: int
    uuid: UUID
    name: str
    type: str
    description: str
    version: str
    icon: str
    namespace: str
    enabled: bool
    local_only: bool
