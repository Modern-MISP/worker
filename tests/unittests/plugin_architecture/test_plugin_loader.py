import inspect
import os
import sys
import unittest

from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from mmisp.worker.plugins.loader import PluginLoader
from plugins.enrichment_plugins import dummy_plugin


class TestPluginImport(unittest.TestCase):
    _plugin_factory: EnrichmentPluginFactory = EnrichmentPluginFactory()

    def test_load_plugin(self):
        dummy_plugin_path: str = str(dummy_plugin.__file__)
        PluginLoader.load_plugins([dummy_plugin_path], self._plugin_factory)
        if os.name == 'nt':
            self.assertTrue(
                any(dummy_plugin_path.replace('\\', '\\\\') in str(module) for module in sys.modules.values())
            )

        # Check if the plugin has been loaded.
        else:
            self.assertTrue(any(dummy_plugin_path in str(module) for module in sys.modules.values()))

        # Check if the plugin has been registered in the factory.
        registered: bool = False
        for plugin_module in self._plugin_factory._plugins.values():
            if dummy_plugin_path in str(inspect.getmodule(plugin_module).__file__):
                registered = True
                break

        self.assertTrue(registered)

    def test_load_plugins_from_directory(self):
        dns_resolver_path: str = str(os.path.join(os.path.dirname(dummy_plugin.__file__), "dns_resolver.py"))
        assert not any(dns_resolver_path in str(module) for module in sys.modules.values()), \
            f"The plugin '{dns_resolver_path}' must not be loaded yet."

        PluginLoader.load_plugins_from_directory(os.path.dirname(dns_resolver_path), self._plugin_factory)

        if os.name == 'nt':
            self.assertTrue(
                any(dns_resolver_path.replace('\\','\\\\') in str(module) for module in sys.modules.values())
            )

        # Check if the plugin has been loaded.
        else:
            self.assertTrue(any(dns_resolver_path in str(module) for module in sys.modules.values()))

        # Check if the plugin 'dns_resolver.py' in the directory has been detected and loaded.
