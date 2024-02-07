from datetime import datetime
from typing import Any, Union, Optional, Dict
from uuid import UUID

from pydantic import ConfigDict, NonNegativeInt, Field, \
    field_validator, BaseModel, StringConstraints, UUID5, UUID4, UUID3, UUID1, conlist, model_serializer
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT, TINYINT, VARCHAR
from sqlmodel import SQLModel, Field as SQLModelField
from typing_extensions import Annotated

from mmisp.worker.misp_dataclasses.misp_id import MispId
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, AttributeTagRelationship


class MispEventAttribute(BaseModel):
    """
    Encapsulates an MISP Event-Attribute.
    """

    model_config: ConfigDict = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    id: MispId | None = None
    event_id: MispId
    object_id: MispId
    object_relation: Annotated[str, StringConstraints(max_length=255)] | None = None
    category: Annotated[str, StringConstraints(max_length=255)]
    type: Annotated[str, StringConstraints(max_length=100)]
    to_ids: bool = True
    uuid: Union[UUID1, UUID3, UUID4, UUID5] | None = None
    timestamp: datetime | None = None
    distribution: Annotated[int, Field(ge=0, le=5)]
    sharing_group_id: MispId | None = None
    comment: Annotated[str, StringConstraints(max_length=65535)] | None = None
    deleted: bool = False
    disable_correlation: bool = False
    first_seen: str | None = None
    last_seen: str | None = None
    value: Annotated[str, StringConstraints(max_length=131071)]
    event_uuid: Union[UUID1, UUID3, UUID4] | None = None
    data: str = None
    tags: conlist(tuple[MispTag, AttributeTagRelationship]) = []

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, value) -> Any:
        if value == "":
            return None

        return value

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        """
        Serializes the MispTag to a dictionary used for json serialization.

        :return: returns the MispTag as a dictionary.
        :rtype: Dict[str, Any]
        """
        return {'id': self.id,
                'event_id': self.event_id,
                'object_id': self.object_id,
                'object_relation': self.object_relation,
                'category': self.category,
                'type': self.type,
                'to_ids': self.to_ids,
                'uuid': self.uuid,
                'timestamp': int(datetime.timestamp(self.timestamp)),
                'distribution': self.distribution,
                'sharing_group_id': self.sharing_group_id,
                'comment': self.comment,
                'deleted': self.deleted,
                'disable_correlation': self.disable_correlation,
                'first_seen': self.first_seen,
                'last_seen': self.last_seen,
                'value': self.value,
                'event_uuid': self.event_uuid,
                'data': self.data,
                'tags': self.tags
                }


class MispSQLEventAttribute(SQLModel, table=True):
    """
    Encapsulates an MISP Event-Attribute for the MISP SQL database.
    """
    __tablename__ = "attributes"

    model_config: ConfigDict = ConfigDict(str_strip_whitespace=True, str_min_length=1)

    id: Optional[int] = SQLModelField(INTEGER(11), primary_key=True)
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

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, value: Any) -> Any:
        """
        Method to convert an empty string to None for the SQL model.

        :param value:  value to convert
        :type value: Any
        :return: returns None if the input is an empty string, otherwise the input value
        :rtype: Any
        """
        if value == "":
            return None

        return value
