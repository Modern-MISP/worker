from src.api.worker_router.plugin_data import EnrichmentPlugin
from src.worker.enrichment_job.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from src.plugins.loader import load_plugins


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
        return cls.__plugin_factory

    @classmethod
    def get_plugins(cls) -> list[EnrichmentPlugin]:
        pass