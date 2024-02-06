from typing import Any
from uuid import UUID

from pydantic import BaseModel, NonNegativeInt, model_validator, field_validator

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
    date: str | None = None
    threat_level_id: int
    info: str | None = None
    published: bool
    uuid: UUID
    attribute_count: int | None = None
    analysis: int
    timestamp: NonNegativeInt
    distribution: int
    proposal_email_lock: bool | None = None
    locked: bool | None = None
    publish_timestamp: NonNegativeInt | None = None
    sharing_group_id: int | None = None
    disable_correlation: bool | None = None
    extends_uuid: UUID | None = None
    protected: str | None = None
    event_creator_email: str | None = None

    org: MispOrganisation | None = None
    orgc: MispOrganisation | None = None

    # TODO remove None after we tested with bonoboAPI
    attributes: list[MispEventAttribute] | None = None
    shadow_attributes: list[MispProposal] | None = None
    related_events: list["MispEvent"] | None = None
    clusters: list[MispGalaxy] | None = None
    objects: list[MispObject] | None = None
    reports: list[MispEventReport] | None = None
    tags: list[tuple[MispTag, EventTagRelationship]] | None = None
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

    @field_validator('uuid', mode='before')
    @classmethod
    def empty_str_to_none(cls, value) -> Any:
        if value == "" or value is None or value == "0":
            return UUID("00000000-0000-0000-0000-000000000000")

        return value

    @field_validator('extends_uuid', mode='before')
    @classmethod
    def empty_str_to_none(cls, value) -> Any:
        if value == "" or value is None or value == "0":
            return UUID("00000000-0000-0000-0000-000000000000")

        return value
