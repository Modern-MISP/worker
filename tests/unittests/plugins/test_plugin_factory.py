import unittest

from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.plugins.plugin import PluginInfo
from plugins.enrichment_plugins import dummy_plugin, dns_resolver
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from plugins.enrichment_plugins.dummy_plugin import DummyPlugin


class TestPluginFactory(unittest.TestCase):

    def test_register(self):
        dummy_plugin.register(enrichment_plugin_factory)
        self.assertTrue(DummyPlugin in enrichment_plugin_factory._plugins.values())

    def test_unregister(self):
        dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
        dummy_plugin.register(enrichment_plugin_factory)
        self.assertTrue(enrichment_plugin_factory.is_plugin_registered(dummy_plugin_name))
        enrichment_plugin_factory.unregister(DummyPlugin.PLUGIN_INFO.NAME)
        self.assertFalse(enrichment_plugin_factory.is_plugin_registered(dummy_plugin_name))
        with self.assertRaises(PluginNotFound):
            enrichment_plugin_factory.unregister("random_not_existing_plugin_name")

    def test_get_plugin(self):
        dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
        dummy_plugin.register(enrichment_plugin_factory)
        self.assertTrue(DummyPlugin.PLUGIN_INFO == enrichment_plugin_factory.get_plugin_info(dummy_plugin_name))
        with self.assertRaises(PluginNotFound):
            enrichment_plugin_factory.unregister("random_not_existing_plugin_name")

    def test_get_plugins(self):
        dummy_plugin.register(enrichment_plugin_factory)
        dns_resolver.register(enrichment_plugin_factory)
        loaded_plugins: list[PluginInfo] = enrichment_plugin_factory.get_plugins()
        self.assertTrue(DummyPlugin.PLUGIN_INFO in loaded_plugins)
        self.assertTrue(DNSResolverPlugin.PLUGIN_INFO in loaded_plugins)

    def test_is_plugin_registered(self):
        dummy_plugin.register(enrichment_plugin_factory)
        self.assertTrue(enrichment_plugin_factory.is_plugin_registered(DummyPlugin.PLUGIN_INFO.NAME))
        self.assertFalse(enrichment_plugin_factory.is_plugin_registered("random_not_existing_plugin_name"))
        with self.assertRaises(PluginNotFound):
            enrichment_plugin_factory.unregister("random_not_existing_plugin_name")
