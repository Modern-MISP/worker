import unittest

from mmisp.worker.exceptions.plugin_exceptions import PluginNotFound, PluginRegistrationError, NotAValidPlugin
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from mmisp.worker.plugins.plugin import PluginInfo
from plugins.enrichment_plugins import dummy_plugin, dns_resolver
from plugins.enrichment_plugins.dns_resolver import DNSResolverPlugin
from plugins.enrichment_plugins.dummy_plugin import DummyPlugin


class TestPluginFactory(unittest.TestCase):
    _plugin_factory: EnrichmentPluginFactory = EnrichmentPluginFactory()

    def test_register(self):
        self._plugin_factory.register(DummyPlugin)
        self.assertIn(DummyPlugin, self._plugin_factory._plugins.values())

    def test_register_invalid_plugin(self):
        class InvalidPlugin:
            pass

        with self.assertRaises(NotAValidPlugin):
            self._plugin_factory.register(InvalidPlugin)

    def test_register_existing_plugin_name(self):
        class DummyPluginClone:
            PLUGIN_INFO: PluginInfo = DummyPlugin.PLUGIN_INFO

        with self.assertRaises(PluginRegistrationError):
            self._plugin_factory.register(DummyPluginClone)

    def test_unregister(self):
        dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
        dummy_plugin.register(self._plugin_factory)
        self.assertTrue(self._plugin_factory.is_plugin_registered(dummy_plugin_name))
        self._plugin_factory.unregister(DummyPlugin.PLUGIN_INFO.NAME)
        self.assertFalse(self._plugin_factory.is_plugin_registered(dummy_plugin_name))
        with self.assertRaises(PluginNotFound):
            self._plugin_factory.unregister("random_not_existing_plugin_name")

    def test_get_plugin_info(self):
        dummy_plugin_name: str = DummyPlugin.PLUGIN_INFO.NAME
        dummy_plugin.register(self._plugin_factory)
        self.assertEquals(DummyPlugin.PLUGIN_INFO, self._plugin_factory.get_plugin_info(dummy_plugin_name))
        with self.assertRaises(PluginNotFound):
            self._plugin_factory.get_plugin_info("random_not_existing_plugin_name")

    def test_get_plugins(self):
        dummy_plugin.register(self._plugin_factory)
        dns_resolver.register(self._plugin_factory)
        loaded_plugins: list[PluginInfo] = self._plugin_factory.get_plugins()
        self.assertIn(DummyPlugin.PLUGIN_INFO, loaded_plugins)
        self.assertIn(DNSResolverPlugin.PLUGIN_INFO, loaded_plugins)

    def test_is_plugin_registered(self):
        dummy_plugin.register(self._plugin_factory)
        self.assertRaises(ValueError, self._plugin_factory.is_plugin_registered, "")
        self.assertFalse(self._plugin_factory.is_plugin_registered("random_not_existing_plugin_name"))
        self.assertTrue(self._plugin_factory.is_plugin_registered(DummyPlugin.PLUGIN_INFO.NAME))
