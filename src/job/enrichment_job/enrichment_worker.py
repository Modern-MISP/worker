from src.api.worker_router.plugin_data import EnrichmentPlugin
from src.job.enrichment_job.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from src.plugins.loader import load_plugins


class EnrichmentWorker:
    """
    Encapsulates a Worker for the enrichment jobs.

    The job is responsible for loading enrichment plugins and providing access to the factory.
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
