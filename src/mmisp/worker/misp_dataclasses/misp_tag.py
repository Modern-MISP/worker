from typing import Union

from pydantic import BaseModel, StringConstraints, UUID4, UUID1, UUID3, UUID5
from pydantic_core import PydanticCustomError
from sqlmodel import SQLModel, Field
from typing_extensions import Annotated

from mmisp.worker.misp_dataclasses.misp_id import MispId

from sqlalchemy import Column, Date, DateTime, Index, LargeBinary, String, Table, Text, VARBINARY, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER, LONGTEXT, MEDIUMTEXT, SMALLINT, TEXT, TINYINT, VARCHAR


"""
class MispTag(BaseModel):
    
    Encapsulates a MISP Tag attachable to Events and Attributes.
    

    id: MispId
    name: Annotated[str, StringConstraints(min_length=1, max_length=255)] | None = None
    colour: Annotated[str, StringConstraints(pattern="^#[0-9a-fA-F]{6}$")] | None = None
    exportable: bool = True
    org_id: MispId
    user_id: MispId
    hide_tag: bool = False
    numerical_value: int | None = None
    is_galaxy: bool = True
    is_custom_galaxy: bool = True
    local_only: bool = True
    inherited: Annotated[int, Field(le=2**31-1)]

    @model_validator(mode='after')
    def validate_tag(self):
        mandatory_alt1: list = [self.id]
        mandatory_alt2: list = [self.name, self.colour, self.org_id, self.user_id]

        if all(mandatory_alt1) or all(mandatory_alt2):
            return
        else:
            raise PydanticCustomError("Not enough values specified.",
                                      "Please provide an id of an already existing tag or a name, \
                                      colour, org-id and user-id so that a new tag can be created.")

"""


class MispTag(SQLModel, table=True):
    __tablename__ = 'tags'

    id: int = Field(INTEGER(11), primary_key=True)
    name: str = Column(VARCHAR(255), nullable=False, unique=True)
    colour: str = Column(VARCHAR(7), nullable=False)
    exportable: bool = Column(TINYINT(1), nullable=False)
    org_id: int = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
    user_id: int = Column(INTEGER(11), nullable=False, index=True, server_default=text("0"))
    hide_tag: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    numerical_value: int = Column(INTEGER(11), index=True)
    is_galaxy: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    is_custom_galaxy: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))
    local_only: bool = Column(TINYINT(1), nullable=False, server_default=text("0"))



class EventTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event and a Tag.
    """

    event_id: MispId | Union[UUID1, UUID3, UUID4, UUID5]
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None


class AttributeTagRelationship(BaseModel):
    """
    Encapsulates a relationship between a MISP Event-Attribute and a Tag.
    """

    attribute_id: MispId | Union[UUID1, UUID3, UUID4, UUID5] | None = None
    tag_id: MispId | None = None
    local: Annotated[int, Field(ge=0, le=1)] | None = None
    relationship_type: Annotated[str, StringConstraints(min_length=1)] | None = None

    def is_complete(self) -> bool:
        return self.attribute_id and self.tag_id
