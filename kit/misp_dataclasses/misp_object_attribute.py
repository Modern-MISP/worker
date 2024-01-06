from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from kit.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from kit.misp_dataclasses.misp_proposal import MispProposal
from kit.misp_dataclasses.misp_sighting import MispSighting


class MispObjectAttribute(BaseModel):
    id: int
    type: str
    category: str
    to_ids: bool
    uuid: UUID
    event_id: str
    distribution: int
    timestamp: datetime
    comment: str
    sharing_group_id: int
    deleted: bool
    disable_correlation: bool
    object_id: int
    object_relation: str
    first_seen: datetime
    last_seen: datetime
    value: str

    galaxies: List[MispGalaxyCluster]
    shadow_attribute: List[MispProposal]
    sightings: List[MispSighting]