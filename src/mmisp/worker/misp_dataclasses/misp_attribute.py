from typing import Union

from pydantic import BaseModel, StringConstraints, ConfigDict, UUID5, UUID4, UUID3, UUID1, NonNegativeInt, Field, \
    conlist
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
