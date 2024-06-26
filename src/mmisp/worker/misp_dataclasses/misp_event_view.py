from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, NonNegativeInt

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_tag import MispTag


class MispMinimalEvent(BaseModel):
    """
    Encapsulates a minimal MISP Event.
    """
    id: int
    timestamp: NonNegativeInt | None = None
    published: bool | None = None
    uuid: str | None = None
    org_c_uuid: str | None = None
