from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR
from sqlmodel import SQLModel, Field

from mmisp.worker.misp_dataclasses import MispGalaxy
from mmisp.worker.misp_dataclasses.misp_galaxy_element import MispGalaxyElement
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation

"""
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
"""


class MispGalaxyCluster(SQLModel, table=True):
    __tablename__ = 'galaxy_clusters'

    id: Optional[int] = Field(INTEGER(11), primary_key=True)
    uuid: UUID = Column(String(255), nullable=False, index=True, server_default=text("''"))
    collection_uuid: str = Column(String(255), nullable=False, index=True)
    type: str = Column(String(255), nullable=False, index=True)
    value: str = Column(Text, nullable=False, index=True)
    tag_name: str = Column(VARCHAR(255), nullable=False, index=True, server_default=text("''"))
    description: str = Column(Text, nullable=False)
    galaxy_id: int = Column(INTEGER(11), nullable=False, index=True)
    source: str = Column(String(255), nullable=False, server_default=text("''"))
    authors: str = Column(Text, nullable=False)  # TODO konvertiermethode?
    version: int = Column(INTEGER(11), index=True, server_default=text("0"))
    distribution: int = Column(TINYINT(4), nullable=False, server_default=text("0"))
    sharing_group_id: int = Column(INTEGER(11), index=True)
    org_id: int = Column(INTEGER(11), nullable=False, index=True)
    orgc_id: int = Column(INTEGER(11), nullable=False, index=True)
    default: bool = Column(TINYINT(1), nullable=False, index=True, server_default=text("0"))
    locked: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    extends_uuid: str = Column(String(40), index=True, server_default=text("''"))
    extends_version: int = Column(INTEGER(11), index=True, server_default=text("0"))
    published: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    deleted: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))

    # TODO adapt to match SQLModel
    galaxy: MispGalaxy
    galaxy_elements: list[MispGalaxyElement]
    galaxy_cluster_relations: list[MispGalaxyElement]
    organisation: MispOrganisation
    organisation_c: MispOrganisation
