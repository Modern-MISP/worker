from typing import List
from uuid import UUID

from pydantic import BaseModel


class MispGalaxyCluster(BaseModel):
    id: int
    uuid: UUID
    collection_uuid: UUID
    type: str
    value: str
    tag_name: str
    description: str
    galaxy_id: int
    source: str
    authors: List[str]
    version: int
    distribution: int
    sharing_group_id: int
    org_id: int
    orgc_id: int
    default: bool
    locked: bool
    extends_uuid: UUID
    extends_version: int
    published: bool
    deleted: bool
