from pydantic import BaseModel, NonNegativeInt


class EnrichAttributeData(BaseModel):
    """
    Encapsulates the necessary data to create an enrich-attribute job.
    """

    class Config:
        """
        Pydantic configuration.
        """

        allow_mutation: bool = False
        anystr_strip_whitespace: bool = True
        min_anystr_length: int = 1

    attribute_id: NonNegativeInt
    """The ID of the attribute to enrich."""
    enrichment_plugins: list[str]
    """The list of enrichment plugins to use for enrichment"""


class EnrichEventData(BaseModel):
    """
    Encapsulates the data needed for an enrich-event job.
    """

    class Config:
        """
        Pydantic configuration.
        """

        allow_mutation: bool = False
        anystr_strip_whitespace: bool = True
        min_anystr_length: int = 1

    event_id: int
    """The ID of the event to enrich."""
    enrichment_plugins: list[str]
    """The list of enrichment plugins to use for enrichment"""


class EnrichEventResult(BaseModel):
    """
    Encapsulates the result of an enrich-event job.

    Contains the number of created attributes.
    """

    created_attributes: NonNegativeInt = 0
    """The number of created attributes."""
