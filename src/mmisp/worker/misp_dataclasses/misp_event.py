from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.mmisp.worker.misp_dataclasses.misp_event_report import MispEventReport
from src.mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from src.mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from src.mmisp.worker.misp_dataclasses.misp_object import MispObject
from src.mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship
from src.mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from src.mmisp.worker.misp_dataclasses.misp_proposal import MispProposal


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
    sharing_group_id: bool
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
