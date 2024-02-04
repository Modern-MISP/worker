import unittest

from mmisp.worker.jobs.enrichment import enrich_attribute_job
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, EventTagRelationship
from mmisp.worker.plugins.plugin import PluginType


class TestEnrichAttributeJob(unittest.TestCase):
    class TestPlugin:
        PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(NAME="TestEnrichAttributeJob-Plugin",
                                                                 PLUGIN_TYPE=PluginType.ENRICHMENT,
                                                                 DESCRIPTION="This is a test plugin.",
                                                                 AUTHOR="John Doe", VERSION="1.0",
                                                                 ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
                                                                 MISP_ATTRIBUTES=PluginIO(INPUT=['hostname', 'domain'],
                                                                                          OUTPUT=['ip-src', 'ip-dst'])
                                                                 )

        TEST_PLUGIN_RESULT: EnrichAttributeResult = (
            EnrichAttributeResult(
                attributes=[MispEventAttribute(event_id=815, object_id=24, category="Network activity",
                                               type="domain", value="www.kit.edu", distribution=2)],
                event_tags=[(MispTag(id=3), EventTagRelationship(event_id=815, tag_id=3))]))

        def __init__(self, misp_attribute: MispEventAttribute):
            self.__misp_attribute = misp_attribute

        def run(self) -> EnrichAttributeResult:
            return self.TEST_PLUGIN_RESULT

    class TestPluginTwo:
        PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(NAME="TestEnrichAttributeJob-PluginTwo",
                                                                 PLUGIN_TYPE=PluginType.ENRICHMENT,
                                                                 DESCRIPTION="This is a test plugin.",
                                                                 AUTHOR="John Doe", VERSION="1.0",
                                                                 ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
                                                                 MISP_ATTRIBUTES=PluginIO(INPUT=['domain', 'ip-dst'],
                                                                                          OUTPUT=['ip-src'])
                                                                 )
        TEST_PLUGIN_RESULT: EnrichAttributeResult = (
            EnrichAttributeResult(
                attributes=[MispEventAttribute(event_id=816, object_id=24, category="Network activity",
                                               type="domain", value="www.kit.edu", distribution=2)],
                event_tags=[(MispTag(id=4), EventTagRelationship(event_id=816, tag_id=4))]))

        def __init__(self, misp_attribute: MispEventAttribute):
            self.__misp_attribute = misp_attribute

        def run(self) -> EnrichAttributeResult:
            return self.TEST_PLUGIN_RESULT

    @classmethod
    def setUpClass(cls):
        enrichment_plugin_factory.register(cls.TestPlugin)
        enrichment_plugin_factory.register(cls.TestPluginTwo)

    def test_enrich_attribute_job(self):
        # TODO: Implement test
        pass

    def test_enrich_attribute(self):
        attribute: MispEventAttribute = MispEventAttribute(event_id=10, object_id=3, category="Network activity",
                                                           type="domain", value="www.google.com",
                                                           distribution=1)

        plugins_to_execute: list[str] = [self.TestPlugin.PLUGIN_INFO.NAME, self.TestPluginTwo.PLUGIN_INFO.NAME]
        result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute(attribute, plugins_to_execute)

        created_attributes: list[MispEventAttribute] = result.attributes
        created_event_tags: list[tuple[MispTag, EventTagRelationship]] = result.event_tags

        expected_attributes: list[MispEventAttribute] = (
                    self.TestPlugin.TEST_PLUGIN_RESULT.attributes +
                    self.TestPluginTwo.TEST_PLUGIN_RESULT.attributes)

        expected_event_tags: list[tuple[MispTag, EventTagRelationship]] = (
                    self.TestPlugin.TEST_PLUGIN_RESULT.event_tags +
                    self.TestPluginTwo.TEST_PLUGIN_RESULT.event_tags)

        self.assertTrue(len(result.attributes) == len(expected_attributes))
        self.assertTrue(all(expected_attribute in created_attributes for expected_attribute in expected_attributes))

        self.assertTrue(len(result.event_tags) == len(expected_event_tags))
        self.assertTrue(all(expected_event_tag in created_event_tags for expected_event_tag in expected_event_tags))

    def test_enrich_attribute_skipping_plugins(self):
        attribute: MispEventAttribute = MispEventAttribute(event_id=10, object_id=4, category="Network activity",
                                                           type="hostname", value="important-host",
                                                           distribution=2)

        plugins_to_execute: list[str] = [self.TestPlugin.PLUGIN_INFO.NAME, self.TestPluginTwo.PLUGIN_INFO.NAME]
        result: EnrichAttributeResult = enrich_attribute_job.enrich_attribute(attribute, plugins_to_execute)

        # Check that only plugins are executed that are compatible with the attribute.
        self.assertTrue(len(result.attributes) == 1)
        self.assertTrue(len(result.event_tags) == 1)
        self.assertTrue(result == self.TestPlugin.TEST_PLUGIN_RESULT)
