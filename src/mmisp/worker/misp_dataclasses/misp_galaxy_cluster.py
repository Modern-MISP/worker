from uuid import UUID

from pydantic import BaseModel

from sqlalchemy import Column, Date, DateTime, Index, LargeBinary, String, Table, Text, VARBINARY, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER, LONGTEXT, MEDIUMTEXT, SMALLINT, TEXT, TINYINT, VARCHAR
from sqlmodel import SQLModel, Field

"""
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
    authors: list[str]
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
"""


class MispGalaxyCluster(SQLModel, table=True):
    __tablename__ = 'galaxy_clusters'

    id: int = Field(INTEGER(11), primary_key=True)
    uuid: UUID = Column(String(255), nullable=False, index=True, server_default=text("''"))
    collection_uuid: UUID = Column(String(255), nullable=False, index=True)
    type: str = Column(String(255), nullable=False, index=True)
    value: str = Column(Text, nullable=False, index=True)
    tag_name: str = Column(VARCHAR(255), nullable=False, index=True, server_default=text("''"))
    description: str = Column(Text, nullable=False)
    galaxy_id: int = Column(INTEGER(11), nullable=False, index=True)
    source: str = Column(String(255), nullable=False, server_default=text("''"))
    authors: str = Column(Text, nullable=False) # TODO konvertiermethode?
    version: int = Column(INTEGER(11), index=True, server_default=text("0"))
    distribution: int = Column(TINYINT(4), nullable=False, server_default=text("0"))
    sharing_group_id: int = Column(INTEGER(11), index=True)
    org_id: int = Column(INTEGER(11), nullable=False, index=True)
    orgc_id: int = Column(INTEGER(11), nullable=False, index=True)
    default: bool = Column(TINYINT(1), nullable=False, index=True, server_default=text("0"))
    locked: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    extends_uuid: UUID = Column(String(40), index=True, server_default=text("''"))
    extends_version: int = Column(INTEGER(11), index=True, server_default=text("0"))
    published: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    deleted: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
