from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses import MispGalaxy
from mmisp.worker.misp_dataclasses.misp_galaxy_element import MispGalaxyElement
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation


class MispGalaxyCluster(BaseModel):
    id: int
    uuid: UUID
    collection_uuid: UUID
    type: str
    value: str
    tag_name: str
    description: str
    source: str
    authors: list[str]
    version: str
    distribution: int
    sharing_group_id: int
    default: bool
    locked: bool
    extends_uuid: UUID
    extends_version: str
    published: bool
    deleted: bool

    galaxy: MispGalaxy
    galaxy_elements: list[MispGalaxyElement]
    galaxy_cluster_relations: list[MispGalaxyElement]
    organisation: MispOrganisation
    organisation_c: MispOrganisation
