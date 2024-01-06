from datetime import datetime

from pydantic import BaseModel

from kit.misp_dataclasses.organisation import Organisation


class Proposal(BaseModel):
    id: int
    old_id: int
    event_id: int
    type: str
    category: str
    uuid: str
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
    org_uuid: str
    old_uuid: str
    event_uuid: str
    organisation: Organisation
