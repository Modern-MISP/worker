import unittest
from typing import Self, cast
from unittest.mock import patch

from mmisp.worker.exceptions.plugin_exceptions import NotAValidPlugin, PluginNotFound
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import (
    EnrichmentPlugin,
    EnrichmentPluginInfo,
    EnrichmentPluginType,
    PluginIO,
)
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute
from mmisp.worker.plugins.plugin import PluginType


class TestEnrichmentPluginFactory(unittest.TestCase):
    __plugin_factory: EnrichmentPluginFactory = EnrichmentPluginFactory()

    class TestPlugin:
        PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
            NAME="Test Plugin",
            PLUGIN_TYPE=PluginType.ENRICHMENT,
            DESCRIPTION="This is a test plugin.",
            AUTHOR="John Doe",
            VERSION="1.0",
            ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
            MISP_ATTRIBUTES=PluginIO(INPUT=["hostname", "domain"], OUTPUT=["ip-src", "ip-dst"]),
        )

        def __init__(self: Self, misp_attribute: MispFullAttribute) -> None:
            self.__misp_attribute = misp_attribute

        # not used in this test
        def run(self: Self) -> EnrichAttributeResult:
            pass

        def test_get_input(self: Self) -> MispFullAttribute:
            return self.__misp_attribute

    @classmethod
    def setUpClass(cls) -> None:
        cls.__plugin_factory.register(cls.TestPlugin)

    def test_create_plugin(self: Self):
        test_plugin_name: str = self.TestPlugin.PLUGIN_INFO.NAME

        test_attribute: MispFullAttribute = MispFullAttribute(
            event_id=4,
            object_id=3,
            category="Network activity",
            type="hostname",
            value="www.google.com",
            comment="",
            to_ids=False,
            distribution=2,
        )
        plugin: EnrichmentPlugin = self.__plugin_factory.create(test_plugin_name, test_attribute)
        self.assertIsInstance(plugin, self.TestPlugin)
        test_plugin = cast(self.TestPlugin, plugin)
        self.assertEqual(test_plugin.test_get_input(), test_attribute)
        with self.assertRaises(PluginNotFound):
            self.__plugin_factory.create("random_not_existing_plugin_name", test_attribute)

    def test_create_invalid_plugin(self: Self):
        with patch.object(self.TestPlugin, "__init__"):
            test_plugin_name: str = self.TestPlugin.PLUGIN_INFO.NAME
            with self.assertRaises(NotAValidPlugin):
                self.__plugin_factory.create(test_plugin_name, None)

    def test_get_plugin_io(self: Self):
        plugin_info: PluginIO = self.__plugin_factory.get_plugin_io(self.TestPlugin.PLUGIN_INFO.NAME)
        self.assertEqual(plugin_info, self.TestPlugin.PLUGIN_INFO.MISP_ATTRIBUTES)
        with self.assertRaises(PluginNotFound):
            self.__plugin_factory.get_plugin_io("random_not_existing_plugin_name")
