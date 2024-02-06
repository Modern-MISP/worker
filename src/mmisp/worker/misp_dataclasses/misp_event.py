from typing import Any
from uuid import UUID

from pydantic import BaseModel, NonNegativeInt, model_validator

from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event_report import MispEventReport
from mmisp.worker.misp_dataclasses.misp_galaxy import MispGalaxy
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship


class MispEvent(BaseModel):
    id: int
    orgc_id: int
    org_id: int
    date: str
    threat_level_id: int
    info: str
    published: bool
    uuid: str
    attribute_count: int
    analysis: int
    timestamp: NonNegativeInt
    distribution: int
    proposal_email_lock: bool
    locked: bool
    publish_timestamp: NonNegativeInt
    sharing_group_id: int
    disable_correlation: bool
    extends_uuid: str
    protected: str | None = None
    event_creator_email: str

    org: MispOrganisation | None = None
    orgc: MispOrganisation | None = None

    # TODO remove None after we tested with bonoboAPI
    attributes: list[MispEventAttribute] | None = None
    shadow_attributes: list[MispProposal] | None = None
    related_events: list["MispEvent"] | None = None
    clusters: list[MispGalaxy] | None = None
    objects: list[MispObject] | None = None
    reports: list[MispEventReport] | None = None
    tags: list[tuple[MispTag, EventTagRelationship]]
    cryptographic_key: list[str] | None = None

    @staticmethod
    def get_uuids_from_events(events: list["MispEvent"]) -> list[UUID]:
        """
        Method to extract a list of UUIDs from a given list of MispEvent.
        :param events: list of MispEvent to get the UUIDs from
        :return: list of UUIDs
        """
        result: list[UUID] = list()
        for event in events:
            result.append(event.uuid)
        return result
