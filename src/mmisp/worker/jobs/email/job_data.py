from datetime import datetime

from pydantic import BaseModel


class AlertEmailData(BaseModel):
    """
    Encapsulates the necessary data to send and create an alert email.
    """

    receiver_ids: list[int]
    """The ids of the receivers"""
    event_id: int
    """The id of the event which triggered the alert"""
    old_publish: datetime
    """The timestamp of old publishing"""


class ContactEmailData(BaseModel):
    """
    Encapsulates the necessary data to send and create a contact email.
    """

    event_id: int
    """The id of the event which the user wants to know more about"""
    message: str
    """The custom message of the user"""
    receiver_ids: list[int]
    """The ids of the receivers"""


class PostsEmailData(BaseModel):
    """
    Encapsulates the necessary data to send and create a posts email.
    """

    post_id: int
    """The id of the post where something new was posted"""
    title: str
    """The title of the post"""
    message: str
    """The message which was posted at the post"""
    receiver_ids: list[int]
    """The ids of the receivers"""
