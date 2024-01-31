from typing import Optional
from uuid import UUID

from pydantic import NonNegativeInt
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT, TINYINT, VARCHAR
from sqlmodel import SQLModel, Field

from mmisp.worker.misp_dataclasses.misp_id import MispId

"""
class MispEventAttribute(BaseModel):
    
    Encapsulates an MISP Event-Attribute.
    

    model_config: ConfigDict = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    id: MispId | None = None
    event_id: MispId
    object_id: MispId
    object_relation: Annotated[str, StringConstraints(max_length=255)] | None = None
    category: Annotated[str, StringConstraints(max_length=255)]
    type: Annotated[str, StringConstraints(max_length=100)]
    to_ids: bool = True
    uuid: Union[UUID1, UUID3, UUID4, UUID5] | None = None
    timestamp: NonNegativeInt
    distribution: Annotated[int, Field(ge=0, le=5)]
    sharing_group_id: MispId | None = None
    comment: Annotated[str, StringConstraints(max_length=65535)]
    deleted: bool = False
    disable_correlation: bool = False
    first_seen: NonNegativeInt | None = None
    last_seen: NonNegativeInt | None = None
    value: Annotated[str, StringConstraints(max_length=131071)]
    event_uuid: Union[UUID1, UUID3, UUID4] | None = None
    data: str = None
    tags: conlist(tuple[MispTag, AttributeTagRelationship]) = []
"""


class MispEventAttribute(SQLModel, table=True):
    __tablename__ = "attributes"

    """
    Encapsulates an MISP Event-Attribute.
    """

    #model_config: ConfigDict = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    id: Optional[int] = Field(INTEGER(11), primary_key=True)
    event_id: MispId = Column(INTEGER(11), nullable=False, index=True)
    object_id: MispId = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
    object_relation: str = Column(String(255), index=True)
    category: str = Column(String(255), nullable=False, index=True)
    type: str = Column(VARCHAR(100), nullable=False, index=True)
    value1: str = Column(TEXT, nullable=False, index=True)
    value2: str = Column(TEXT, nullable=False, index=True)
    to_ids: bool = Column(TINYINT(1), nullable=False, server_default=text("1"))
    uuid: UUID = Column(String(40), nullable=False, unique=True)
    timestamp: NonNegativeInt = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
    distribution: int = Column(TINYINT(4), nullable=False, server_default=text("0"))
    sharing_group_id: MispId = Column(INTEGER(11), nullable=False, index=True)
    comment: str = Column(TEXT)
    deleted: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    disable_correlation: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    first_seen: NonNegativeInt = Column(BIGINT(20), index=True)
    last_seen: NonNegativeInt = Column(BIGINT(20), index=True)
