import os
import sys
import unittest

from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.plugins.loader import PluginLoader
from plugins.enrichment_plugins import dummy_plugin


class TestPluginImport(unittest.TestCase):

    def test_load_plugin(self):
        dummy_plugin_path: str = str(dummy_plugin.__file__)
        PluginLoader.load_plugins([dummy_plugin_path], enrichment_plugin_factory)

        # Check if the plugin has been loaded.
        self.assertTrue(any(dummy_plugin_path in str(module) for module in sys.modules.values()))

        # Check if the plugin has been registered in the factory.
        self.assertTrue(dummy_plugin_path in str(plugin_module.__file__)
                        for plugin_module in enrichment_plugin_factory._plugins.values())

    def test_load_plugins_from_directory(self):
        dns_resolver_path: str = str(os.path.join(os.path.dirname(dummy_plugin.__file__), "dns_resolver.py"))
        assert not any(dns_resolver_path in str(module) for module in sys.modules.values()), \
            f"The plugin '{dns_resolver_path}' must not be loaded yet."

        PluginLoader.load_plugins_from_directory(os.path.dirname(dns_resolver_path), enrichment_plugin_factory)

        # Check if the plugin 'dns_resolver.py' in the directory has been detected and loaded.
        self.assertTrue(any(dns_resolver_path in str(module) for module in sys.modules.values()))
