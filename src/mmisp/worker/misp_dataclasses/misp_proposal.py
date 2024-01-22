from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation


class MispProposal(BaseModel):
    id: int
    old_id: int
    event_id: int
    type: str
    category: str
    uuid: UUID
    to_ids: bool
    comment: str
    org_id: int
    timestamp: datetime
    first_seen: str
    last_seen: str
    deleted: bool
    proposal_to_delete: bool
    disable_correlation: bool
    value: str
    org_uuid: UUID
    old_uuid: UUID
    event_uuid: UUID
    organisation: MispOrganisation
