from datetime import datetime
from typing import List, Self
from uuid import UUID

from pydantic import BaseModel

from kit.misp_dataclasses.misp_event_report import MispEventReport
from kit.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.misp_dataclasses.misp_object import MispObject
from kit.misp_dataclasses.misp_tag import MispTag, EventTagRelationship
from kit.misp_dataclasses.misp_organisation import MispOrganisation
from kit.misp_dataclasses.misp_proposal import MispProposal


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

    attributes: List[MispEventAttribute]
    shadow_attributes: List[MispProposal]
    related_events: List[Self]
    clusters: List[MispGalaxyCluster]
    objects: List[MispObject]
    reports: List[MispEventReport]
    tags: List[(MispTag, EventTagRelationship)]
    cryptographic_key: List[str]

    def to_json(self) -> str:
        pass
