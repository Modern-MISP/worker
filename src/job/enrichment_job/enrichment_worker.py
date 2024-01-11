from src.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginInfo
from src.job.enrichment_job.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from src.plugins.loader import PluginLoader


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
    def get_plugins(cls) -> list[EnrichmentPluginInfo]:
        pass
