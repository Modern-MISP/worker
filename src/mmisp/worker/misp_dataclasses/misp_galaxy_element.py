from pydantic import BaseModel


class MispGalaxyElement(BaseModel):
    """
    Encapsulates a MISP Galaxy Element.
    """
    id: int
    galaxy_cluster_id: int
    key: str
    value: str
