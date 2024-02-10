from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting


class MispObjectAttribute(BaseModel):
    """
    Encapsulates a MISP Object Attribute.
    """
    id: int
    type: str | None = None
    category: str | None = None
    to_ids: bool | None = None
    uuid: UUID
    event_id: int
    distribution: int
    timestamp: datetime
    comment: str
    sharing_group_id: int
    deleted: bool
    disable_correlation: bool | None = None
    object_id: int | None = None
    object_relation: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    value: str | None = None
