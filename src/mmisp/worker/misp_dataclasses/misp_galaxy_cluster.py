from uuid import UUID

from pydantic import BaseModel


class MispGalaxyCluster(BaseModel):
    id: int
    uuid: UUID
    collection_uuid: UUID
    type: str | None = None
    value: str | None = None
    tag_name: str | None = None
    description: str | None = None
    galaxy_id: int
    source: str | None = None
    authors: list[str] | None = None
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
