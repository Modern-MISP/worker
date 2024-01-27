from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_event_report import MispEventReport
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal


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
