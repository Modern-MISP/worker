import unittest
from http.client import HTTPException
from typing import Self, Type
from unittest.mock import patch

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute, NewEventTag
from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.plugins.plugin_type import PluginType
from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.exceptions.job_exceptions import JobException
from mmisp.worker.exceptions.misp_api_exceptions import APIException
from mmisp.worker.jobs.enrichment import enrich_attribute_job
from mmisp.worker.jobs.enrichment.enrichment_worker import enrichment_worker
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeData
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock
from tests.unittests.jobs.enrichment.plugins.passthrough_plugin import PassthroughPlugin


class TestEnrichAttributeJob(unittest.TestCase):
    class TestPlugin:
        PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
            NAME="TestEnrichAttributeJob-Plugin",
            PLUGIN_TYPE=PluginType.ENRICHMENT,
            DESCRIPTION="This is a test plugin.",
            AUTHOR="John Doe",
            VERSION="1.0",
            ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
            MISP_ATTRIBUTES=PluginIO(INPUT=["hostname", "domain"], OUTPUT=["ip-src", "ip-dst"]),
        )

        TEST_PLUGIN_RESULT: EnrichAttributeResult = EnrichAttributeResult(
            attributes=[
                NewAttribute(
                    attribute=AddAttributeBody(
                        event_id=815,
                        object_id=24,
                        category="Network activity",
                        type="domain",
                        value="www.kit.edu",
                        distribution=2,
                    )
                )
            ],
            event_tags=[NewEventTag(tag_id=3)],
        )

        def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
            self.__misp_attribute = misp_attribute

        def run(self: Self) -> EnrichAttributeResult:
            return self.TEST_PLUGIN_RESULT

    class TestPluginTwo:
        PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
            NAME="TestEnrichAttributeJob-PluginTwo",
            PLUGIN_TYPE=PluginType.ENRICHMENT,
            DESCRIPTION="This is a test plugin.",
            AUTHOR="John Doe",
            VERSION="1.0",
            ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
            MISP_ATTRIBUTES=PluginIO(INPUT=["domain", "ip-dst"], OUTPUT=["ip-src"]),
        )
        TEST_PLUGIN_RESULT: EnrichAttributeResult = EnrichAttributeResult(
            attributes=[
                NewAttribute(
                    attribute=AddAttributeBody(
                        event_id=816,
                        object_id=24,
                        category="Network activity",
                        type="domain",
                        value="www.kit.edu",
                        distribution=2,
                    )
                )
            ],
            event_tags=[NewEventTag(tag_id=4)],
        )

        def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
            self.__misp_attribute = misp_attribute

        def run(self: Self) -> EnrichAttributeResult:
            return self.TEST_PLUGIN_RESULT

    EXAMPLE_ATTRIBUTE: AttributeWithTagRelationship = AttributeWithTagRelationship(
        id=1,
        event_id=10,
        event_uuid="c53e97d1-2202-4988-beb1-e701f25e2218",
        object_id=3,
        object_relation=None,
        category="Network activity",
        type="domain",
        value="www.google.com",
        uuid="d93ada78-3538-40c4-bde9-e85dafa316f8",
        timestamp=1718046516,
        first_seen=1718046516,
        last_seen=1718046516,
        sharing_group_id=1,
        comment="",
        to_ids=False,
        distribution=1,
    )

    @classmethod
    def setUpClass(cls: Type["TestEnrichAttributeJob"]) -> None:
        enrichment_plugin_factory.register(cls.TestPlugin)
        enrichment_plugin_factory.register(cls.TestPluginTwo)
        enrichment_plugin_factory.register(PassthroughPlugin)

    @patch("mmisp.worker.jobs.enrichment.enrich_attribute_job.enrichment_worker")
    def test_enrich_attribute_job(self: Self, enrichment_worker_mock):
        enrichment_worker_mock.misp_api = MispAPIMock()

        attribute_id: int = 12
        job_data: EnrichAttributeData = EnrichAttributeData(
            attribute_id=attribute_id, enrichment_plugins=[PassthroughPlugin.PLUGIN_INFO.NAME]
        )

        result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute_job(UserData(user_id=0), job_data)
        self.assertEqual(result.attributes[0], MispAPIMock()._get_event_attribute(attribute_id))

    def test_enrich_attribute(self: Self):
        plugins_to_execute: list[str] = [self.TestPlugin.PLUGIN_INFO.NAME, self.TestPluginTwo.PLUGIN_INFO.NAME]
        result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute(
            self.EXAMPLE_ATTRIBUTE, plugins_to_execute
        )

        created_attributes: list[NewAttribute] = result.attributes
        created_event_tags: list[NewEventTag] = result.event_tags

        expected_attributes: list[NewAttribute] = (
            self.TestPlugin.TEST_PLUGIN_RESULT.attributes + self.TestPluginTwo.TEST_PLUGIN_RESULT.attributes
        )

        expected_event_tags: list[NewEventTag] = (
            self.TestPlugin.TEST_PLUGIN_RESULT.event_tags + self.TestPluginTwo.TEST_PLUGIN_RESULT.event_tags
        )

        self.assertEqual(len(created_attributes), len(expected_attributes))
        self.assertTrue(all(expected_attribute in created_attributes for expected_attribute in expected_attributes))

        self.assertEqual(len(created_event_tags), len(expected_event_tags))
        self.assertTrue(all(expected_event_tag in created_event_tags for expected_event_tag in expected_event_tags))

    def test_enrich_attribute_with_faulty_plugins(self: Self):
        attribute: AttributeWithTagRelationship = AttributeWithTagRelationship(
            id=1,
            event_id=10,
            event_uuid="c53e97d1-2202-4988-beb1-e701f25e2218",
            object_id=4,
            object_relation=None,
            category="Network activity",
            type="domain",
            value="important-host",
            uuid="d93ada78-3538-40c4-bde9-e85dafa316f8",
            timestamp=1718046516,
            first_seen=1718046516,
            last_seen=1718046516,
            sharing_group_id=1,
            comment="",
            to_ids=False,
            distribution=2,
        )

        plugins_to_execute: list[str] = [
            "Unknown Plugin",
            self.TestPlugin.PLUGIN_INFO.NAME,
            self.TestPluginTwo.PLUGIN_INFO.NAME,
            PassthroughPlugin.PLUGIN_INFO.NAME,
        ]

        with (
            patch.object(enrichment_plugin_factory, "get_plugin_io") as plugin_io_mock,
            patch.object(self.TestPlugin, "__init__") as test_plugin_mock,
            patch.object(self.TestPluginTwo, "run") as test_plugin_two_mock,
            patch.object(PassthroughPlugin, "run", autospec=True) as passthrough_plugin_mock,
        ):
            plugin_io_mock.return_value = PluginIO(INPUT=["domain"], OUTPUT=["domain"])
            test_plugin_mock.side_effect = lambda: ()
            test_plugin_two_mock.side_effect = TypeError("Any error in plugin execution.")
            enrich_attribute_job.enrich_attribute(attribute, plugins_to_execute)

        self.assertTrue(test_plugin_mock.called)
        self.assertTrue(test_plugin_two_mock.called)
        self.assertTrue(passthrough_plugin_mock.called)

    def test_enrich_attribute_skipping_plugins(self: Self):
        attribute: AttributeWithTagRelationship = AttributeWithTagRelationship(
            id=1,
            event_id=10,
            event_uuid="c53e97d1-2202-4988-beb1-e701f25e2218",
            object_id=4,
            object_relation=None,
            category="Network activity",
            type="hostname",
            value="important-host",
            uuid="d93ada78-3538-40c4-bde9-e85dafa316f8",
            timestamp=1718046516,
            first_seen=1718046516,
            last_seen=1718046516,
            sharing_group_id=1,
            comment="",
            to_ids=False,
            distribution=2,
        )

        plugins_to_execute: list[str] = [self.TestPlugin.PLUGIN_INFO.NAME, self.TestPluginTwo.PLUGIN_INFO.NAME]
        result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute(attribute, plugins_to_execute)

        # Check that only plugins are executed that are compatible with the attribute.
        self.assertEqual(len(result.attributes), 1)
        self.assertEqual(len(result.event_tags), 1)
        self.assertEqual(result, self.TestPlugin.TEST_PLUGIN_RESULT)

    def test_enrich_attribute_job_api_exceptions(self: Self):
        self.test_enrich_attribute_job()
        with patch.object(enrichment_worker.misp_api, "get_event_attribute") as misp_api_mock:
            for exception in [APIException, HTTPException]:
                misp_api_mock.side_effect = exception("")
                with self.assertRaises(JobException):
                    enrich_attribute_job.enrich_attribute_job(
                        UserData(user_id=1), EnrichAttributeData(attribute_id=1, enrichment_plugins=["TestPlugin"])
                    )
