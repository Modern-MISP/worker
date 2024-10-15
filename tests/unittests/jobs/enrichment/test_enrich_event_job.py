import unittest
from http.client import HTTPException
from typing import Self, Type
from unittest.mock import Mock, patch

from mmisp.api_schemas.tags import TagViewResponse
from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment import enrich_event_job
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData, EnrichEventResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock
from tests.unittests.jobs.enrichment.plugins.passthrough_plugin import PassthroughPlugin

# TODO : FIX Variables
AttributeTagRelationship = None
EventTagRelationship = None


class TestEnrichEventJob(unittest.TestCase):
    @classmethod
    def setUpClass(cls: Type["TestEnrichEventJob"]) -> None:
        enrichment_plugin_factory.register(PassthroughPlugin)

    def test_enrich_event_job(self: Self):
        api_mock: Mock = Mock(spec=MispAPIMock, autospec=True)

        event_id: int = 1
        input_attributes: list[AttributeWithTagRelationship] = [
            AttributeWithTagRelationship(
                id=1,
                event_id=event_id,
                object_id=1,
                category="Network activity",
                type="domain",
                distribution=0,
                value="www.kit.edu",
                tags=[
                    (
                        TagViewResponse(id=1, name="Hallo", colour="#FF0000", org_id=3, user_id=1),
                        AttributeTagRelationship(attribute_id=event_id, tag_id=1),
                    )
                ],
            )
        ]

        api_mock.get_event_attributes.return_value = input_attributes

        new_tags_plugin_name: str = PassthroughPlugin.PLUGIN_INFO.NAME
        input_data: EnrichEventData = EnrichEventData(event_id=event_id, enrichment_plugins=[new_tags_plugin_name])

        enrich_attribute_result: EnrichAttributeResult = EnrichAttributeResult(
            attributes=input_attributes,
            event_tags=[
                (
                    TagViewResponse(name="new_event_tag", colour="#FF0000", org_id=3, user_id=1),
                    EventTagRelationship(event_id=event_id, relationship_type="friend"),
                )
            ],
        )
        # Todo Amadeus
        enrich_attribute_result.attributes[0].Tag.append(
            (
                TagViewResponse(name="new_attribute_tag", colour="#FF0000", org_id=3, user_id=1),
                AttributeTagRelationship(
                    attribute_id=enrich_attribute_result.attributes[0].id, relationship_type="friend"
                ),
            )
        )

        with (
            patch(
                "mmisp.worker.jobs.enrichment.enrich_event_job.enrichment_worker", autospec=True
            ) as enrichment_worker_mock,
            patch(
                "mmisp.worker.jobs.enrichment.enrich_event_job.enrich_attribute", autospec=True
            ) as enrich_attribute_mock,
            patch(
                "mmisp.worker.jobs.enrichment.enrich_event_job._create_attribute", autospec=True
            ) as create_attribute_mock,
            patch(
                "mmisp.worker.jobs.enrichment.enrich_event_job._write_event_tag", autospec=True
            ) as write_event_tag_mock,
        ):
            enrichment_worker_mock.misp_api = api_mock
            enrich_attribute_mock.return_value = enrich_attribute_result

            result: EnrichEventResult = enrich_event_job.enrich_event_job(UserData(user_id=0), input_data)

            api_mock.get_event_attributes.assert_called_once_with(event_id)
            enrich_attribute_mock.assert_called_with(input_attributes[0], input_data.enrichment_plugins)
            create_attribute_mock.assert_called_with(enrich_attribute_result.attributes[0])
            write_event_tag_mock.assert_called_with(enrich_attribute_result.event_tags[0])
            self.assertEqual(result.created_attributes, len(enrich_attribute_result.attributes))

    def test_enrich_event_job_with_api_exceptions(self: Self):
        with patch(
            "mmisp.worker.jobs.enrichment.enrich_event_job.enrichment_worker.misp_api.get_event_attributes"
        ) as api_mock:
            for exception in [APIException, HTTPException]:
                api_mock.side_effect = exception("Any error in API call.")
                with self.assertRaises(JobException):
                    enrich_event_job.enrich_event_job(
                        UserData(user_id=0), EnrichEventData(event_id=1, enrichment_plugins=["TestPlugin"])
                    )

    def test_create_attribute(self: Self):
        existing_attribute_tag: tuple[TagViewResponse, AttributeTagRelationship] = (
            TagViewResponse(id=1),
            AttributeTagRelationship(tag_id=1, relationship_type="friend"),
        )

        new_attribute_tag: tuple[TagViewResponse, AttributeTagRelationship] = (
            TagViewResponse(name="new_attribute_tag", colour="#FF0000", org_id=3, user_id=1),
            AttributeTagRelationship(relationship_type="friend"),
        )

        input_attribute: AttributeWithTagRelationship = AttributeWithTagRelationship(
            event_id=1,
            object_id=1,
            category="Network activity",
            type="domain",
            distribution=0,
            value="www.kit.edu",
            tags=[existing_attribute_tag, new_attribute_tag],
        )

        with patch(
            "mmisp.worker.jobs.enrichment.enrich_event_job.enrichment_worker", autospec=True
        ) as enrichment_worker_mock:
            api: MispAPIMock = MispAPIMock()
            sql: MispSQLMock = MispSQLMock()

            api_mock: Mock = Mock(wraps=api, spec=MispAPIMock, autospec=True)
            sql_mock: Mock = Mock(wraps=sql, spec=MispSQLMock, autospec=True)
            enrichment_worker_mock.misp_api = api_mock
            enrichment_worker_mock.misp_sql = sql_mock

            enrich_event_job._create_attribute(input_attribute)
            api_mock.create_attribute.assert_called_with(input_attribute)

            attribute_id: int = api.create_attribute(input_attribute)

            # Test if the new_attribute_tag is created correctly before attaching to the attribute.
            api_mock.create_tag.assert_called_with(new_attribute_tag[0])
            new_attribute_tag_id: int = api.create_tag(new_attribute_tag[0])

            new_attribute_tag[0].id = new_attribute_tag_id
            new_attribute_tag[1].tag_id = new_attribute_tag_id

            # Test if the attribute tags are attached correctly to the attribute.
            for tag in input_attribute.Tag:
                prepared_attribute_tag: tuple[TagViewResponse, AttributeTagRelationship] = tag
                prepared_attribute_tag[1].attribute_id = attribute_id

                api_mock.attach_attribute_tag.assert_called_with(prepared_attribute_tag[1])
                sql_mock.get_attribute_tag_id.assert_called_with(attribute_id, prepared_attribute_tag[1].tag_id)
                attribute_tag_id: int = sql.get_attribute_tag_id(attribute_id, prepared_attribute_tag[1].tag_id)
                prepared_attribute_tag[1].id = attribute_tag_id
                api_mock.modify_attribute_tag_relationship.assert_called_with(prepared_attribute_tag[1])

    def test_write_event_tag(self: Self):
        existing_event_tag: tuple[TagViewResponse, EventTagRelationship] = (
            TagViewResponse(id=1),
            EventTagRelationship(event_id=1, tag_id=1, relationship_type="friend"),
        )

        new_event_tag: tuple[TagViewResponse, EventTagRelationship] = (
            TagViewResponse(name="new_event_tag", colour="#FF0000", org_id=3, user_id=1),
            EventTagRelationship(event_id=1, relationship_type="friend"),
        )

        with patch(
            "mmisp.worker.jobs.enrichment.enrich_event_job.enrichment_worker", autospec=True
        ) as enrichment_worker_mock:
            api: MispAPIMock = MispAPIMock()
            sql: MispSQLMock = MispSQLMock()

            api_mock: Mock = Mock(wraps=api, spec=MispAPIMock, autospec=True)
            sql_mock: Mock = Mock(wraps=sql, spec=MispSQLMock, autospec=True)
            enrichment_worker_mock.misp_api = api_mock
            enrichment_worker_mock.misp_sql = sql_mock

            # Test if a new event-tag is created correctly before attaching it to the event.
            enrich_event_job._write_event_tag(new_event_tag)
            api_mock.create_tag.assert_called_with(new_event_tag[0])
            new_event_tag[1].id = api.create_tag(new_event_tag[0])
            api_mock.attach_event_tag.assert_called_with(new_event_tag[1])

            # Test if a tag is attached correctly to the event.
            enrich_event_job._write_event_tag(existing_event_tag)

            relationship: EventTagRelationship = existing_event_tag[1]

            api_mock.attach_event_tag.assert_called_with(relationship)
            sql_mock.get_event_tag_id(relationship.event_id, relationship.tag_id)
            relationship.id = sql.get_event_tag_id(relationship.event_id, relationship.tag_id)
            api_mock.modify_event_tag_relationship.assert_called_with(relationship)
