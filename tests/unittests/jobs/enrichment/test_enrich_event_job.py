import random
import unittest
from http.client import HTTPException
from typing import Self, Type
from unittest.mock import Mock, patch

from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute, NewTag
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.tests.generators.attribute_generator import generate_attribute_with_tag_relationship
from mmisp.tests.generators.object_generator import generate_random_str, generate_valid_random_object_create_attributes
from mmisp.tests.generators.tag_generator import (
    generate_exising_new_tag,
    generate_new_new_tag,
    generate_valid_tag_data,
)
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment import enrich_event_job
from mmisp.worker.jobs.enrichment.job_data import EnrichEventData, EnrichEventResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.misp_database.misp_api import MispAPI
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.mocks.misp_database_mock.misp_sql_mock import MispSQLMock
from tests.unittests.jobs.enrichment.plugins.passthrough_plugin import PassthroughPlugin


class TestEnrichEventJob(unittest.TestCase):
    @classmethod
    def setUpClass(cls: Type["TestEnrichEventJob"]) -> None:
        enrichment_plugin_factory.register(PassthroughPlugin)

    def test_enrich_event_job(self: Self):
        api_mock: Mock = Mock(spec=MispAPI, autospec=True)
        input_attributes: list[AttributeWithTagRelationship] = [generate_attribute_with_tag_relationship()]
        event_id: int = input_attributes[0].event_id
        api_mock.get_event_attributes.return_value = input_attributes

        new_tags_plugin_name: str = PassthroughPlugin.PLUGIN_INFO.NAME
        input_data: EnrichEventData = EnrichEventData(event_id=event_id,
                                                      enrichment_plugins=[new_tags_plugin_name])

        enrich_attribute_result: EnrichAttributeResult = EnrichAttributeResult(
            attributes=[NewAttribute(attribute=generate_valid_random_object_create_attributes())],
            event_tags=[NewTag(tag=generate_valid_tag_data(), relationship=generate_random_str())]
        )

        enrich_attribute_result.attributes[0].tags.append(
            NewTag(tag=generate_valid_tag_data(), relationship_type=generate_random_str())
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
        new_attribute: NewAttribute = NewAttribute(attribute=generate_valid_random_object_create_attributes())
        existing_attribute_tag: NewTag = generate_exising_new_tag()
        new_attribute_tag: NewTag = generate_new_new_tag()
        new_attribute.tags.extend([existing_attribute_tag, new_attribute_tag])

        with patch(
                "mmisp.worker.jobs.enrichment.enrich_event_job.enrichment_worker", autospec=True
        ) as enrichment_worker_mock:
            api: MispAPIMock = MispAPIMock()
            sql: MispSQLMock = MispSQLMock()

            api_mock: Mock = Mock(wraps=api, spec=MispAPIMock, autospec=True)
            sql_mock: Mock = Mock(wraps=sql, spec=MispSQLMock, autospec=True)
            enrichment_worker_mock.misp_api = api_mock
            enrichment_worker_mock.misp_sql = sql_mock

            enrich_event_job._create_attribute(new_attribute)
            api_mock.create_attribute.assert_called_with(new_attribute)

            attribute_id: int = api.create_attribute(new_attribute.attribute)

            # Test if the new_attribute_tag is created correctly before attaching to the attribute.
            api_mock.create_tag.assert_called_with(new_attribute_tag)

            new_attribute_tag.tag_id = api.create_tag(new_attribute_tag.tag)

            # Test if the attribute tags are attached correctly to the attribute.
            for tag in new_attribute.tags:
                api_mock.attach_attribute_tag.assert_called_with(attribute_id, new_attribute_tag.tag_id,
                                                                 new_attribute_tag.local)
                api_mock.attach_attribute_tag.assert_called_with(attribute_id, existing_attribute_tag.tag_id,
                                                                 new_attribute_tag.local)
                sql_mock.get_attribute_tag_id.assert_called_with(attribute_id, new_attribute_tag.tag_id)
                sql_mock.get_attribute_tag_id.assert_called_with(attribute_id, existing_attribute_tag.tag_id)
                attribute_tag_id: int = sql.get_attribute_tag_id(attribute_id, new_attribute_tag.tag_id)
                api_mock.modify_attribute_tag_relationship.assert_called_with(new_attribute_tag.tag_id,
                                                                              existing_attribute_tag.relationship_type)
                attribute_tag_id: int = sql.get_attribute_tag_id(attribute_id, new_attribute_tag.tag_id)
                api_mock.modify_attribute_tag_relationship.assert_called_with(new_attribute_tag.tag_id,
                                                                              existing_attribute_tag.relationship_type)

    def test_write_event_tag(self: Self):
        existing_event_tag: NewTag = generate_exising_new_tag()
        new_event_tag: NewTag = generate_new_new_tag()

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
            event_id: int = random.randint(1, 20)
            enrich_event_job._write_event_tag(event_id, new_event_tag)
            api_mock.create_tag.assert_called_with(new_event_tag.tag)
            new_event_tag.tag_id = api.create_tag(new_event_tag.tag)
            api_mock.attach_event_tag.assert_called_with(event_id, new_event_tag.tag_id, new_event_tag.local)

            # Test if a tag is attached correctly to the event.
            enrich_event_job._write_event_tag(event_id, existing_event_tag)
            api_mock.attach_event_tag.assert_called_with(event_id, existing_event_tag.tag_id, existing_event_tag.local)
            sql_mock.get_event_tag_id(event_id, existing_event_tag.tag_id)
            event_tag_id = sql.get_event_tag_id(event_id, existing_event_tag.tag_id)
            api_mock.modify_event_tag_relationship.assert_called_with(event_id, existing_event_tag.relationship_type)
