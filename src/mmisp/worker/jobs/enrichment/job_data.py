from pydantic import BaseModel, ConfigDict, NonNegativeInt, conlist

from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship


class EnrichAttributeData(BaseModel):
    """
    Encapsulates the necessary data to create an enrich-attribute jobs
    """

    model_config: ConfigDict = ConfigDict(frozen=True, str_strip_whitespace=True, str_min_length=1)

    attribute_id: NonNegativeInt
    """The ID of the attribute to enrich."""
    enrichment_plugins: conlist(str, min_length=1)
    """The list of enrichment plugins to use for enrichment"""


class EnrichEventData(BaseModel):
    """
    Encapsulates the data needed for an enrich-event job.
    """

    model_config: ConfigDict = ConfigDict(frozen=True, str_strip_whitespace=True, str_min_length=1)

    event_id: int
    """The ID of the event to enrich."""
    enrichment_plugins: conlist(str, min_length=1)
    """The list of enrichment plugins to use for enrichment"""


class EnrichAttributeResult(BaseModel):
    """
    Encapsulates the result of an enrich-attribute job.

    Contains newly created attributes and tags.
    """
    attributes: list[MispEventAttribute] = []
    """The created attributes."""
    event_tags: list[tuple[MispTag, EventTagRelationship]] = []
    """The created event tags. Can also be already existing tags."""

    def append(self, result_to_merge: 'EnrichAttributeResult'):
        """
        Merges two EnrichAttributeResult objects together.

        :param result_to_merge: The object that should be merged into this result.
        :type result_to_merge: EnrichAttributeResult
        """
        self.attributes.extend(result_to_merge.attributes)
        self.event_tags.extend(result_to_merge.event_tags)


class EnrichEventResult(BaseModel):
    """
    Encapsulates the result of an enrich-event job.

    Contains the number of created attributes.
    """
    created_attributes: NonNegativeInt = 0
    """The number of created attributes."""
