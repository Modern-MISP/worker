
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation

from datetime import datetime

from sqlalchemy import Column, DateTime, TEXT, String, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR, BIGINT
from sqlmodel import SQLModel, Field

"""
class MispSighting(BaseModel):
    id: int
    attribute_id: int
    event_id: int
    org_id: int
    date_sighting: datetime
    uuid: UUID
    source: str
    type: int
    attribute_uuid: UUID
    organisation: MispOrganisation
"""


class MispSighting(SQLModel, table=True):
    __tablename__ = 'sightings'

    id: int = Field(INTEGER(11), primary_key=True)
    attribute_id: int = Column(INTEGER(11), nullable=False, index=True)
    event_id: int = Column(INTEGER(11), nullable=False, index=True)
    org_id: int = Column(INTEGER(11), nullable=False, index=True)
    date_sighting: datetime = Column(BIGINT(20), nullable=False)
    uuid: UUID = Column(String(255), unique=True, server_default=text("''"))
    source: str = Column(String(255), index=True, server_default=text("''"))
    type: int = Column(INTEGER(11), index=True, server_default=text("0"))
