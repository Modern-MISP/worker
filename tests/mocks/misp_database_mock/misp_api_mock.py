import datetime
import uuid
from typing import Any, Self
from unittest.mock import AsyncMock

from mmisp.api_schemas.attributes import AddAttributeBody, GetAllAttributesResponse
from mmisp.api_schemas.events import (
    AddEditGetEventAttribute,
    AddEditGetEventDetails,
    AddEditGetEventOrg,
    AddEditGetEventTag,
)
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.tags import TagCreateBody


class MispAPIMock(AsyncMock):
    def __init__(self: Self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def get_event(self: Self, event_id: int, server: Server = None) -> AddEditGetEventDetails:
        tags: list[AddEditGetEventTag] = [
            AddEditGetEventTag(
                id=1,
                name="tlp:white",
                colour="#ffffff",
                exportable=True,
                user_id=1,
                hide_tag=False,
                numerical_value=12345,
                is_galaxy=True,
                is_custom_galaxy=True,
                local_only=True,
                local=True,
            )
        ]

        match event_id:
            case 1:
                return AddEditGetEventDetails(
                    id=1,
                    org_id=1,
                    date="2023 - 11 - 16",
                    info="sdfas",
                    uuid="fb2fa4a266e548a39bdd5c5ce78e11e8",
                    extends_uuid="fb2fa4a266e548a39bdd5c5ce78e11e8",
                    published=False,
                    analysis=0,
                    attribute_count=6,
                    orgc_id=1,
                    timestamp=1706736785,
                    distribution=4,
                    sharing_group_id=1,
                    proposal_email_lock=False,
                    locked=False,
                    threat_level_id=1,
                    publish_timestamp=1700496633,
                    sighting_timestamp=0,
                    disable_correlation=False,
                    protected=None,
                    event_creator_email="",
                    attributes=[self._get_event_attribute_old(1)],
                    related_events=[self.get_event(2)],  # attention: recursive call
                    Object=[self.get_object(1)],
                    Tag=tags,
                    Org=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                    Orgc=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                )
            # attention: get_event(2) is called in get_event(1)
            case 2:
                return AddEditGetEventDetails(
                    id=2,
                    org_id=1,
                    date="2023-11-16",
                    info="sdfas",
                    uuid="5019f511811a4dab800c80c92bc16d3d",
                    extends_uuid="5019f511811a4dab800c80c92bc16d3d",
                    published=False,
                    analysis=0,
                    attribute_count=6,
                    orgc_id=1,
                    timestamp=1706736785,
                    distribution=4,
                    sharing_group_id=0,
                    proposal_email_lock=False,
                    locked=False,
                    threat_level_id=1,
                    publish_timestamp=1700496633,
                    sighting_timestamp=0,
                    disable_correlation=False,
                    protected=None,
                    event_creator_email="",
                    Attribute=[self._get_event_attribute_old(1)],
                    Object=[self.get_object(1)],
                    Tag=tags,
                    Org=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                    Orgc=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                )

            case 3:
                return AddEditGetEventDetails(
                    id=1,
                    org_id=1,
                    date="2023 - 11 - 16",
                    info="sdfas",
                    uuid="fb2fa4a266e548a39bdd5c5ce78e11e8",
                    extends_uuid="fb2fa4a266e548a39bdd5c5ce78e11e8",
                    published=False,
                    analysis=0,
                    attribute_count=6,
                    orgc_id=1,
                    timestamp=1706736785,
                    distribution=4,
                    sharing_group_id=0,
                    proposal_email_lock=False,
                    locked=False,
                    threat_level_id=1,
                    publish_timestamp=1700496633,
                    sighting_timestamp=0,
                    disable_correlation=False,
                    protected=None,
                    event_creator_email="",
                    Attribute=[self._get_event_attribute_old(1)],
                    RelatedEvent=[self.get_event(2)],  # attention: recursive call
                    Object=[self.get_object(1)],
                    Org=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                    Orgc=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                )
            # attention: get_event(2) is called in get_event(3)
            case 66:
                return AddEditGetEventDetails(
                    id=66,
                    org_id=1,
                    date="2023-11-16",
                    info="sdfas",
                    uuid="5019f511811a4dab800c80c92bc16d3d",
                    extends_uuid="5019f511811a4dab800c80c92bc16d3d",
                    published=False,
                    analysis=0,
                    attribute_count=6,
                    orgc_id=1,
                    timestamp=1706736785,
                    distribution=4,
                    sharing_group_id=0,
                    proposal_email_lock=False,
                    locked=False,
                    threat_level_id=1,
                    publish_timestamp=1700496633,
                    sighting_timestamp=0,
                    disable_correlation=False,
                    protected=None,
                    event_creator_email="",
                    Attribute=[self._get_event_attribute_old(1)],
                    Object=[self.get_object(66)],
                    Tag=tags,
                    Org=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                    Orgc=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                )
            case 69:
                return AddEditGetEventDetails(
                    id=69,
                    org_id=1,
                    date="2023-11-16",
                    info="sdfas",
                    uuid="5019f511811a4dab800c80c92bc16d3d",
                    extends_uuid="5019f511811a4dab800c80c92bc16d3d",
                    published=False,
                    analysis=0,
                    attribute_count=6,
                    orgc_id=1,
                    timestamp=1706736785,
                    distribution=4,
                    sharing_group_id=0,
                    proposal_email_lock=False,
                    locked=False,
                    threat_level_id=1,
                    publish_timestamp=1700496633,
                    sighting_timestamp=0,
                    disable_correlation=False,
                    protected=None,
                    event_creator_email="",
                    Attribute=[self._get_event_attribute_old(1)],
                    Object=[self.get_object(66)],
                    Tag=tags,
                    Org=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                    Orgc=AddEditGetEventOrg(id=1, name="ORGNAME", uuid="5019f511811a4dab800c80c92bc16d3d", local=True),
                )

    def _get_event_attribute_old(self: Self, attribute_id: int) -> AddEditGetEventAttribute:
        attribute: AddEditGetEventAttribute = AddEditGetEventAttribute(
            id=1,
            event_id=20,
            object_id=3,
            object_relation="act-as",
            category="Other",
            type="text",
            to_ids=False,
            uuid="40817bc9-123e-43da-a5e1-aa15a9a4ea6d",
            timestamp=1700088063,
            distribution=0,
            sharing_group_id=0,
            comment="No comment",
            deleted=False,
            disable_correlation=False,
            first_seen="2023-11-23T00:00:00.000000+00:00",
            last_seen="2023-11-23T00:00:00.000000+00:00",
            value="Very important information.",
            Tag=[
                AddEditGetEventTag(
                    id=2,
                    name="tlp:white",
                    colour="#ffffff",
                    exportable=True,
                    user_id=1,
                    hide_tag=False,
                    numerical_value=12345,
                    is_galaxy=True,
                    is_custom_galaxy=True,
                    local_only=True,
                    local=True,
                ),
            ],
        )

        match attribute_id:
            case 1:
                return attribute
            case 12:
                attribute.type = "Any"
                return attribute

    def create_attribute(self: Self, attribute: AddAttributeBody, server: Server = None) -> int:
        return 1

    def create_tag(self: Self, tag: TagCreateBody, server: Server = None) -> int:
        return 1

    def get_object(self: Self, object_id: int, server: Server = None) -> ObjectWithAttributesResponse:
        match object_id:
            case 1:
                return ObjectWithAttributesResponse(
                    id=1,
                    name="TestObject",
                    meta_category="TestMetaCategory",
                    description="TestDescription",
                    template_uuid="123e4567-e89b-12d3-a456-426614174000",
                    template_version=1,
                    event_id=1,
                    uuid="123e4567-e89b-12d3-a456-426614174000",
                    timestamp=1700988063,
                    distribution=1,
                    sharing_group_id=1,
                    comment="TestComment",
                    deleted=False,
                    first_seen=str(datetime.datetime(1, 1, 1)),
                    last_seen=str(datetime.datetime(1, 1, 1)),
                    attributes=[
                        GetAllAttributesResponse(
                            id=1,
                            event_id=1,
                            object_id=1,
                            object_relation="TestObjectRelation",
                            category="TestCategory",
                            type="TestType",
                            to_ids=True,
                            uuid="123e4567-e89b-12d3-a456-426614174000",
                            timestamp=1700978063,
                            distribution=1,
                            sharing_group_id=1,
                            comment="TestComment",
                            deleted=False,
                            disable_correlation=False,
                            first_seen=str(datetime.datetime(1, 1, 1)),
                            last_seen=str(datetime.datetime(1, 1, 1)),
                            value="TestValue",
                        )
                    ],
                )
        match object_id:
            case 66:
                return ObjectWithAttributesResponse(
                    id=66,
                    name="test",
                    meta_category="test",
                    description="test",
                    template_uuid=uuid.uuid4(),
                    template_version=1,
                    event_id=66,
                    uuid=uuid.uuid4(),
                    timestamp=str(datetime.datetime(1, 1, 1)),
                    distribution=1,
                    sharing_group_id=1,
                    comment="test",
                    deleted=False,
                    first_seen=str(datetime.datetime(1, 1, 1)),
                    last_seen=str(datetime.datetime(1, 1, 1)),
                    attributes=[],
                )
