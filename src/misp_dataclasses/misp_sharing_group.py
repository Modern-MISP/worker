from uuid import UUID

from pydantic import BaseModel


class MispSharingGroup(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: str
    releasability: str
    local: bool
    active: bool
    org_count: int
    organisation_uuid: UUID
    org_id: int
    sync_user_id: int
    created: str
    modified: str
    roaming: bool
