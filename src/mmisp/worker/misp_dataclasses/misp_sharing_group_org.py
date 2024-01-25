from uuid import UUID

from pydantic import BaseModel


class MispSharingGroupOrg(BaseModel):
    id: int
    sharing_group_id: int
    org_id: int
    extend: bool
    org_name: str
    org_uuid: UUID
