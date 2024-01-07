from kit.worker.enrichment_worker.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from kit.plugins.loader import load_plugins


class EnrichWorker:
    """
    Encapsulates a Worker for the enrichment jobs.

    The worker is responsible for loading enrichment plugins and providing access to the factory.
    """

    __plugin_factory = EnrichmentPluginFactory()

    @classmethod
    def load_enrichment_plugins(cls):
        pass

    @classmethod
    def get_plugin_factory(cls) -> EnrichmentPluginFactory:
        return cls.plugin_factory
