import unittest

from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from mmisp.worker.plugins.plugin import PluginInfo
from plugins.enrichment_plugins import dummy_plugin, dns_resolver
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from plugins.enrichment_plugins.dummy_plugin import DummyPlugin


class TestPluginFactory(unittest.TestCase):
    __plugin_factory: EnrichmentPluginFactory = EnrichmentPluginFactory()

    def test_register(self):
        dummy_plugin.register(self.__plugin_factory)
        self.assertTrue(DummyPlugin in self.__plugin_factory._plugins.values())

    def test_unregister(self):
        dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
        dummy_plugin.register(self.__plugin_factory)
        self.assertTrue(self.__plugin_factory.is_plugin_registered(dummy_plugin_name))
        self.__plugin_factory.unregister(DummyPlugin.PLUGIN_INFO.NAME)
        self.assertFalse(self.__plugin_factory.is_plugin_registered(dummy_plugin_name))
        with self.assertRaises(PluginNotFound):
            self.__plugin_factory.unregister("random_not_existing_plugin_name")

    def test_get_plugin(self):
        dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
        dummy_plugin.register(self.__plugin_factory)
        self.assertTrue(DummyPlugin.PLUGIN_INFO == self.__plugin_factory.get_plugin_info(dummy_plugin_name))
        with self.assertRaises(PluginNotFound):
            self.__plugin_factory.unregister("random_not_existing_plugin_name")

    def test_get_plugins(self):
        dummy_plugin.register(self.__plugin_factory)
        dns_resolver.register(self.__plugin_factory)
        loaded_plugins: list[PluginInfo] = self.__plugin_factory.get_plugins()
        self.assertTrue(DummyPlugin.PLUGIN_INFO in loaded_plugins)
        self.assertTrue(DNSResolverPlugin.PLUGIN_INFO in loaded_plugins)

    def test_is_plugin_registered(self):
        dummy_plugin.register(self.__plugin_factory)
        self.assertTrue(self.__plugin_factory.is_plugin_registered(DummyPlugin.PLUGIN_INFO.NAME))
        self.assertFalse(self.__plugin_factory.is_plugin_registered("random_not_existing_plugin_name"))
        with self.assertRaises(PluginNotFound):
            self.__plugin_factory.unregister("random_not_existing_plugin_name")
