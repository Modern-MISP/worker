from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from mmisp.worker.misp_dataclasses.misp_event_report import MispEventReport
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal

from sqlalchemy import Column, Date, DateTime, Index, LargeBinary, String, Table, Text, VARBINARY, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER, LONGTEXT, MEDIUMTEXT, SMALLINT, TEXT, TINYINT, VARCHAR

"""
class MispEvent(BaseModel):
    id: int
    orgc_id: int
    org_id: int
    date: str
    threat_level_id: int
    info: str
    published: bool
    uuid: UUID
    attribute_count: int
    analysis: int
    timestamp: datetime
    distribution: int
    proposal_email_lock: bool
    locked: bool
    publish_timestamp: bool
    sharing_group_id: int
    disable_correlation: bool
    extends_uuid: UUID
    protected: str
    event_creator_email: str
    org: MispOrganisation
    orgc: MispOrganisation

    attributes: list[MispEventAttribute]
    shadow_attributes: list[MispProposal]
    related_events: list["MispEvent"]
    clusters: list[MispGalaxyCluster]
    objects: list[MispObject]
    reports: list[MispEventReport]
    tags: list[tuple[MispTag, EventTagRelationship]]
    cryptographic_key: list[str]
"""




class MispEvent(SQLModel, table=True):
    __tablename__ = 'events'

    id: int = Field(INTEGER(11), primary_key=True)
    org_id: int = Column(INTEGER(11), nullable=False, index=True)
    date: str = Column(Date, nullable=False)
    info: str = Column(Text, nullable=False, index=True)
    user_id: int = Column(INTEGER(11), nullable=False)
    uuid: UUID = Column(String(40), nullable=False, unique=True)
    published: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    analysis: int = Column(TINYINT(4), nullable=False)
    attribute_count: int = Column(INTEGER(11), server_default=text("0"))
    orgc_id: int = Column(INTEGER(11), nullable=False, index=True)
    timestamp: datetime = Column(INTEGER(11), nullable=False, server_default=text("0"))
    distribution: int = Column(TINYINT(4), nullable=False, server_default=text("0"))
    sharing_group_id: int = Column(INTEGER(11), nullable=False, index=True)
    proposal_email_lock: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    locked: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    threat_level_id: int = Column(INTEGER(11), nullable=False)
    publish_timestamp: datetime = Column(INTEGER(11), nullable=False, server_default=text("0"))
    sighting_timestamp: datetime = Column(INTEGER(11), nullable=False, server_default=text("0"))
    disable_correlation: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    extends_uuid: UUID = Column(String(40), index=True, server_default=text("''"))
    protected: bool = Column(TINYINT(1))

    @staticmethod
    def get_uuids_from_events(events: list["MispEvent"]) -> list[UUID]:
        # TODO fragen ob hier richtig
        """
        Method to extract a list of UUIDs from a given list of MispEvent.
        :param events: list of MispEvent to get the UUIDs from
        :return: list of UUIDs
        """
        result: list[UUID] = list()
        for event in events:
            result.append(event.uuid)
        return result
