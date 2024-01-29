from typing import Union, Any

from pydantic import BaseModel, StringConstraints, ConfigDict, UUID5, UUID4, UUID3, UUID1, NonNegativeInt, Field, \
    conlist, field_validator
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
    timestamp: NonNegativeInt | None = None
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
