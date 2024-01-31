from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation

from sqlalchemy import Column, DateTime, TEXT, String, text, Text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR, BIGINT
from sqlmodel import SQLModel, Field

"""
class MispProposal(BaseModel):
    id: int
    old_id: int
    event_id: int
    type: str
    category: str
    uuid: UUID
    to_ids: bool
    comment: str
    org_id: int
    timestamp: datetime
    first_seen: str
    last_seen: str
    deleted: bool
    proposal_to_delete: bool
    disable_correlation: bool
    value: str
    org_uuid: UUID
    old_uuid: UUID
    event_uuid: UUID
    organisation: MispOrganisation
    """


class MispProposal(SQLModel, table=True):
    __tablename__ = 'shadow_attributes'

    id: int = Field(INTEGER(11), primary_key=True)
    old_id: int = Column(INTEGER(11), index=True, server_default=text("0"))
    event_id: int = Column(INTEGER(11), nullable=False, index=True)
    type: str = Column(VARCHAR(100), nullable=False, index=True)
    category: str = Column(String(255), nullable=False, index=True)
    value1: str = Column(Text, index=True)
    to_ids: bool = Column(TINYINT(1), nullable=False, server_default=text("1"))
    uuid: UUID = Column(String(40), nullable=False, index=True)
    value2: str = Column(Text, index=True)
    org_id: int = Column(INTEGER(11), nullable=False)
    email: str = Column(VARCHAR(255))
    event_org_id: int = Column(INTEGER(11), nullable=False, index=True)
    comment: str = Column(TEXT, nullable=False)
    event_uuid: UUID = Column(String(40), nullable=False, index=True)
    deleted: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    timestamp: datetime = Column(INTEGER(11), nullable=False, server_default=text("0"))
    proposal_to_delete: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    disable_correlation: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    first_seen: str = Column(BIGINT(20), index=True)
    last_seen: str = Column(BIGINT(20), index=True)
