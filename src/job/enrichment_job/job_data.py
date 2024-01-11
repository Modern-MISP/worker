from pydantic import BaseModel

from src.misp_dataclasses.misp_attribute import MispEventAttribute
from src.misp_dataclasses.misp_tag import MispTag, EventTagRelationship


class EnrichAttributeData(BaseModel):
    """
    Encapsulates the necessary data to create an enrich-attribute job.
    """
    attribute_id: int
    enrichment_plugins: list[str]


class EnrichEventData(BaseModel):
    """
    Encapsulates the data needed for an enrich-event job.
    """
    event_id: int
    enrichment_plugins: list[str]


class EnrichAttributeResult(BaseModel):
    """
    Encapsulates the result of an enrich-attribute job.

    Contains newly created attributes and tags.
    """
    attributes: list[MispEventAttribute]
    event_tags: list[tuple[MispTag, EventTagRelationship]]


class EnrichEventResult(BaseModel):
    """
    Encapsulates the result of an enrich-event job.

    Contains the number of created attributes.
    """
    created_attributes: int
