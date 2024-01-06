from kit.worker.enrichment_worker.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from kit.plugins.loader import load_plugins


class EnrichWorker:

    def __init__(self):
        self.plugin_factory = EnrichmentPluginFactory()
        # Load Plugins

    def get_plugin_factory(self) -> EnrichmentPluginFactory:
        pass
