from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_galaxy_element import MispGalaxyElement
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_tag import MispTag


class MispGalaxyCluster(BaseModel):
    """
    Encapsulates a MISP Galaxy Cluster.
    """
    id: int
    uuid: str
    collection_uuid: str | None = None
    type: str | None = None
    value: str | None = None
    tag_name: str | None = None
    description: str | None = None
    source: str | None = None
    authors: list[str]
    version: str | None = None
    distribution: int
    sharing_group_id: int | None = None
    default: bool
    locked: bool
    extends_uuid: str | None = None
    extends_version: str | None = None
    published: bool
    deleted: bool
    galaxy_elements: list[MispGalaxyElement] = []
    galaxy_cluster_relations: list[MispTag] = []
    organisation: MispOrganisation | None = None
    organisation_c: MispOrganisation | None = None
