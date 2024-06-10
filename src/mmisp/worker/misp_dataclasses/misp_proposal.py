from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation


class ShadowAttribute(BaseModel):
    """
    Encapsulates a MISP Proposal.
    """
    id: int
    old_id: int
    event_id: int
    type: str | None = None
    category: str | None = None
    uuid: str | None = None
    to_ids: bool
    comment: str | None = None
    org_id: int
    timestamp: str
    first_seen: str | None = None
    last_seen: str | None = None
    deleted: bool
    proposal_to_delete: bool
    disable_correlation: bool
    value: str | None = None
    org_uuid: str
    old_uuid: str
    old_uuid: str | None = None
    event_uuid: str | None = None
    Org: MispOrganisation
