from pydantic import BaseModel, NonNegativeInt


class MispMinimalEvent(BaseModel):
    """
    Encapsulates a minimal MISP Event.
    """

    id: int
    timestamp: NonNegativeInt
    published: bool | None = None
    uuid: str | None = None
    org_c_uuid: str | None = None
