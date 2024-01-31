from datetime import datetime

from sqlalchemy import Column, DateTime, TEXT
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR
from sqlmodel import SQLModel, Field

"""
class MispPost(BaseModel):
    id: int
    date_created: datetime
    date_modified: datetime
    user_id: int
    contents: str
    post_id: int
    thread_id: int
    """


class MispPost(SQLModel, table=True):
    __tablename__ = 'posts'

    id: int = Field(INTEGER(11), primary_key=True)
    date_created: datetime = Column(DateTime, nullable=False)
    date_modified: datetime = Column(DateTime, nullable=False)
    user_id: int = Column(INTEGER(11), nullable=False)
    contents: str = Column(TEXT, nullable=False)
    post_id: int = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
    thread_id: int = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
