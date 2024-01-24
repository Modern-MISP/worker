from mmisp.worker.jobs.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginInfo
from mmisp.worker.jobs.enrichment_job.plugins.enrichment_plugin_factory import EnrichmentPluginFactory
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_database.mmisp_redis import MMispRedis
from mmisp.worker.plugins.loader import PluginLoader


class EnrichmentWorker:

    def __init__(self):
        self.misp_api: MispAPI = MispAPI()
        self.misp_sql: MispSQL = MispSQL()
        self.misp_redis: MMispRedis = MMispRedis()
        pass

    """
    Encapsulates a Worker for the enrichment jobs.

    The jobs is responsible for loading enrichment plugins and providing access to the factory.
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


enrichment_worker: EnrichmentWorker = EnrichmentWorker()
