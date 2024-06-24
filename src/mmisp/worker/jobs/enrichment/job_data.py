from typing import Self

from pydantic import BaseModel, ConfigDict, NonNegativeInt

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship
from mmisp.worker.misp_dataclasses.event_tag_relationship import EventTagRelationship


class EnrichAttributeData(BaseModel):
    """
    Encapsulates the necessary data to create an enrich-attribute jobs
    """

    model_config: ConfigDict = ConfigDict(frozen=True, str_strip_whitespace=True, str_min_length=1)

    attribute_id: NonNegativeInt
    """The ID of the attribute to enrich."""
    enrichment_plugins: list[str]
    """The list of enrichment plugins to use for enrichment"""


class EnrichEventData(BaseModel):
    """
    Encapsulates the data needed for an enrich-event job.
    """

    model_config: ConfigDict = ConfigDict(frozen=True, str_strip_whitespace=True, str_min_length=1)

    event_id: int
    """The ID of the event to enrich."""
    enrichment_plugins: list[str]
    """The list of enrichment plugins to use for enrichment"""


class NewAttributeTag(BaseModel):
    """
    Encapsulates a MISP Tag and its assignment to an attribute.
    """

    tag_id: int | None = None
    """The ID of the tag if it already exists in the database."""
    tag: TagCreateBody | None = None
    """The tag if it doesn't exist yet in the Database."""
    relationship: AttributeTagRelationship
    """The assignment and relationship to the attribute."""


class NewAttribute(BaseModel):
    """
    Encapsulates a newly created attribute from the enrichment process.
    """

    attribute: AddAttributeBody
    """The attribute"""
    tags: list[NewAttributeTag] = []
    """Tags attached to the attribute"""


class NewEventTag(BaseModel):
    """
    Encapsulates a MISP Tag assigned to an event.
    """

    tag_id: int | None = None
    """The ID of the tag if it already exists in the database."""
    tag: TagCreateBody | None = None
    """The tag if it doesn't exist yet in the Database."""
    relationship: EventTagRelationship
    """The assignment and relationship to the event."""


class EnrichAttributeResult(BaseModel):
    """
    Encapsulates the result of an enrich-attribute job.

    Contains newly created attributes and tags.
    """

    attributes: list[NewAttribute] = []
    """The created attributes."""
    event_tags: list[NewEventTag] = []
    """The created event tags. Can also be the IDs of already existing tags."""

    def append(self: Self, result_to_merge: "EnrichAttributeResult"):
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
