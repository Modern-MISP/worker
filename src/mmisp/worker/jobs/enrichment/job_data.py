from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship


class EnrichAttributeData(BaseModel):
    """
    Encapsulates the necessary data to create an enrich-attribute jobs.
    """
    attribute_id: int
    enrichment_plugins: list[str]


class EnrichEventData(BaseModel):
    """
    Encapsulates the data needed for an enrich-event jobs.
    """
    event_id: int
    enrichment_plugins: list[str]


class EnrichAttributeResult(BaseModel):
    """
    Encapsulates the result of an enrich-attribute jobs.

    Contains newly created attributes and tags.
    """
    attributes: list[MispEventAttribute]
    event_tags: list[tuple[MispTag, EventTagRelationship]]


class EnrichEventResult(BaseModel):
    """
    Encapsulates the result of an enrich-event jobs.

    Contains the number of created attributes.
    """
    created_attributes: int
