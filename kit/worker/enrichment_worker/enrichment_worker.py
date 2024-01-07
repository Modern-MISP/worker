from kit.worker.enrichment_worker.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from kit.plugins.loader import load_plugins


class EnrichWorker:
    """
    Encapsulates a Worker for the enrichment jobs.

    The worker is responsible for loading enrichment plugins and providing access to the factory.
    """

    plugin_factory = EnrichmentPluginFactory()

    def __init__(self):
        # Load Plugins
        pass

    def get_plugin_factory(self) -> EnrichmentPluginFactory:
        pass
