from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer


class ViewUpdateSharingGroupLegacyResponse(BaseModel):
    """
    Encapsulates a MISP Sharing Group.
    """
    id: int
    uuid: UUID
    name: str
    description: str
    releasability: str
    local: bool
    active: bool
    roaming: bool

    created: str | None = None
    modified: str | None = None
    sync_user_id: int | None = None

    sharing_group_servers: list[MispSharingGroupServer]
    sharing_group_orgs: list[MispSharingGroupOrg]
