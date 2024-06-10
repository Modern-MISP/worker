from datetime import datetime
from typing import Any, Union, Dict

from pydantic import ConfigDict, Field, \
    field_validator, BaseModel, StringConstraints, UUID5, UUID4, UUID3, UUID1, conlist, model_serializer
from typing_extensions import Annotated

from mmisp.api_schemas.tags.get_tag_response import TagViewResponse
from mmisp.worker.misp_dataclasses.misp_id import MispId
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship


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
    data: str | None = None
    Tag: conlist(tuple[TagViewResponse, AttributeTagRelationship]) = []

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
                'timestamp': int(datetime.timestamp(self.timestamp)) if self.timestamp else None,
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
                'tags': self.Tag
                }
