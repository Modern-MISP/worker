from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR
from sqlmodel import SQLModel, Field

"""
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
    """


class MispThread(SQLModel, table=True):
    __tablename__ = 'threads'

    id: int = Field(INTEGER(11), primary_key=True)
    date_created: datetime = Column(DateTime, nullable=False)
    date_modified: datetime = Column(DateTime, nullable=False)
    distribution: int = Column(TINYINT(4), nullable=False)
    user_id: int = Column(INTEGER(11), nullable=False, index=True)
    post_count: int = Column(INTEGER(11), nullable=False)
    event_id: int = Column(INTEGER(11), nullable=False, index=True)
    title: str = Column(VARCHAR(255), nullable=False)
    org_id: int = Column(INTEGER(11), nullable=False, index=True)
    sharing_group_id: int = Column(INTEGER(11), nullable=False, index=True)
