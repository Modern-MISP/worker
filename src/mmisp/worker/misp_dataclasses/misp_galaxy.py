from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator

from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster


class MispGalaxy(BaseModel):
    """
    Encapsulates a MISP Galaxy.
    """
    id: int
    uuid: UUID
    name: str
    type: str
    description: str
    version: str
    icon: str
    namespace: str
    enabled: bool
    local_only: bool
    kill_chain_order: dict | None = None
