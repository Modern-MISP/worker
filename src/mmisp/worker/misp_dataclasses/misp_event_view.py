from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_tag import MispTag


class MispMinimalEvent(BaseModel):
    id: int
    timestamp: datetime
    published: bool
    uuid: UUID
    org_c_uuid: UUID
