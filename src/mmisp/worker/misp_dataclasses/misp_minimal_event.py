from datetime import datetime

from pydantic import BaseModel


class MispMinimalEvent(BaseModel):
    """
    Encapsulates a minimal MISP Event.
    """

    id: int
    timestamp: datetime
    published: bool | None = None
    uuid: str | None = None
    org_c_uuid: str | None = None
