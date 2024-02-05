from uuid import UUID

from pydantic import BaseModel


class MispOrganisation(BaseModel):
    id: int
    uuid: str
    name: str
    local: bool | None = None
