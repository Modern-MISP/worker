from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer


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
    sharing_group_server: MispSharingGroupServer
    sharing_group_orgs: MispSharingGroupOrg
