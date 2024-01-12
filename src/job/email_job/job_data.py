from pydantic import BaseModel


class AlertEmailData(BaseModel):
    receiver_ids: list[int]
    event_id: int
    old_publish: str


class ContactEmailData(BaseModel):
    event_id: int
    message: str
    receiver_ids: list[int]


class PostsEmailData(BaseModel):
    post_id: int
    title: str
    message: str
    receiver_ids: list[int]