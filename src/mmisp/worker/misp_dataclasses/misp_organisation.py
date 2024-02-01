from uuid import UUID

from pydantic import BaseModel


class MispOrganisation(BaseModel):
    id: int
    uuid: UUID
    name: str
    local: bool | None = None
