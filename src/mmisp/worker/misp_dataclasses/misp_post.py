from datetime import datetime

from sqlalchemy import Column, DateTime, TEXT, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR
from sqlmodel import SQLModel, Field

class MispPost(SQLModel, table=True):
    """
    Encapsulates a MISP Post.
    """
    __tablename__ = 'posts'

    id: int = Field(INTEGER(11), primary_key=True)
    date_created: datetime = Column(DateTime, nullable=False)
    date_modified: datetime = Column(DateTime, nullable=False)
    user_id: int = Column(INTEGER(11), nullable=False)
    contents: str = Column(TEXT, nullable=False)
    post_id: int = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
    thread_id: int = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
