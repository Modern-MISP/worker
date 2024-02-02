from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer

from sqlalchemy import Column, Date, DateTime, Index, LargeBinary, String, Table, Text, VARBINARY, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER, LONGTEXT, MEDIUMTEXT, SMALLINT, TEXT, TINYINT, VARCHAR


class MispSharingGroup(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: str
    releasability: str
    local: bool
    active: bool
    roaming: bool

    created: str | None = None
    modified: str | None = None
    sync_user_id: int | None = None

    organisation: MispOrganisation
    sharing_group_servers: list[MispSharingGroupServer]
    sharing_group_orgs: list[MispSharingGroupOrg]



"""
class MispSharingGroup(SQLModel, table=True):
    __tablename__ = 'sharing_groups'

    id: int = Field(INTEGER(11), primary_key=True)
    name: str = Column(VARCHAR(255), nullable=False, unique=True)
    releasability: str = Column(TEXT, nullable=False)
    description: str = Column(TEXT, nullable=False)
    uuid: UUID = Column(String(40), nullable=False, unique=True)
    organisation_uuid: UUID = Column(String(40), nullable=False, index=True)
    org_id: int = Column(INTEGER(11), nullable=False, index=True)
    sync_user_id: int = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
    active: bool = Column(TINYINT(1), nullable=False)
    created: datetime = Column(DateTime, nullable=False)
    modified: datetime = Column(DateTime, nullable=False)
    local: bool = Column(TINYINT(1), nullable=False)
    roaming: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))

    #sharing_group_servers: Optional[list[MispSharingGroupServer]]
    #sharing_group_orgs: Optional[list[MispSharingGroupOrg]]
    """
