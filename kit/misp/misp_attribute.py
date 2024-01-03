from uuid import UUID

from pydantic import BaseModel


class NewEventAttribute(BaseModel):
    """
    Encapsulates a new event-attribute that is not yet created in the MISP-Database.

    Contains all relevant information about an attribute however does not contain a unique ID/UUID,
    representing the attribute or a UUID representing the related event.
    Also, attachments of an attribute aren't part of this class.
    """

    eventId: int
    objectId: int
    objectRelation: str
    category: str
    type: str
    value: str
    toIds: bool
    timestamp: int
    distribution: int
    sharingGroupId: int
    comment: str
    deleted: bool
    disableCorrelation: bool
    firstSeen: int
    lastSeen: int


class EventAttribute(NewEventAttribute):
    """
    Encapsulates a complete MISP event-attribute with all relevant information.
    """

    id: int
    uuid: UUID
    eventUuid: UUID
    data: str
