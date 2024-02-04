
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation

from datetime import datetime


class MispSighting(BaseModel):
    id: int
    attribute_id: int
    event_id: int
    org_id: int
    date_sighting: datetime
    uuid: UUID
    source: str
    type: int
    attribute_uuid: UUID
    organisation: MispOrganisation
