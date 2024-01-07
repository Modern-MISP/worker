from datetime import datetime

from pydantic import BaseModel


class MispPost(BaseModel):
    id: int
    date_created: datetime
    date_modified: datetime
    user_id: int
    contents: str
    post_id: int
    thread_id: int
