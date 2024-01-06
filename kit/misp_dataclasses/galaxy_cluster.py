from typing import List

from pydantic import BaseModel


class GalaxyCluster(BaseModel):
    id: int
    uuid: str
    collection_uuid: str
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
    extends_uuid: str
    extends_version: int
    published: bool
    deleted: bool
