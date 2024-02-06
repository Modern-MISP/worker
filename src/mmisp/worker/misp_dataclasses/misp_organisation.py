from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MispOrganisation(BaseModel):
    id: int
    name: str
    date_created: datetime | None = None
    date_modified: datetime | None = None
    description: str | None = None
    type: str | None = None
    nationality: str | None = None
    sector: str | None = None
    created_by: int | None = None
    uuid: str
    contacts: str | None = None
    local: bool
    restricted_to_domain: list[str] | None = None
    landing_page: str | None = None
    user_count: int | None = None
    created_by_email: str | None = None
