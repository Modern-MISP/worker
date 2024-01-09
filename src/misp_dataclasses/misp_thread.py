from datetime import datetime

from pydantic import BaseModel


class MispThread(BaseModel):
    id: int
    date_created: datetime
    date_modified: datetime
    distribution: int
    user_id: int
    post_count: int
    event_id: int
    title: str
    org_id: int
    sharing_group_id: int

