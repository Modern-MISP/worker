from pydantic import BaseModel


class MispGalaxyElement(BaseModel):
    id: int
    galaxy_cluster_id: int
    key: str
    value: str
