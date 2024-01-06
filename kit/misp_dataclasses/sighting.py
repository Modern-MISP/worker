from datetime import datetime
from pydantic import BaseModel

from kit.misp_dataclasses.organisation import Organisation


class Sighting(BaseModel):
    id: int
    attribute_id: int
    event_id: int
    org_id: int
    date_sighting: datetime
    uuid: str
    source: str
    type: int
    attribute_uuid: str
    organisation: Organisation
