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
    type: str
    category: str
    to_ids: bool
    uuid: UUID
    event_id: int
    distribution: int
    timestamp: datetime
    comment: str
    sharing_group_id: int
    deleted: bool
    disable_correlation: bool
    object_id: int
    object_relation: str
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    value: str

    #galaxies: list[MispGalaxyCluster] TODO löschen falls nimand es braucht
    #shadow_attribute: list[MispProposal] TODO löschen falls nimand es braucht
    #sightings: list[MispSighting] TODO löschen falls nimand es braucht
