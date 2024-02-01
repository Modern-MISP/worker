from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_tag import MispTag


class MispEventView(BaseModel):
    id: int
    date: str
    info: str
    uuid: UUID
    published: bool
    analysis: int
    attribute_count: int
    timestamp: datetime
    distribution: int
    sharing_group_id: int
    proposal_email_lock: bool
    locked: bool
    threat_level_id: int
    publish_timestamp: datetime
    sighting_timestamp: datetime
    disable_correlation: bool
    extends_uuid: UUID
    protected: bool
    organisation: MispOrganisation
    organisation_c: MispOrganisation
    event_tag: MispTag
