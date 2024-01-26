from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.misp_database.misp_api import MispAPI


class EnrichmentWorker:
    """
    Encapsulates a Worker for the enrichment jobs.
    """

    def __init__(self):
        self.__misp_api: MispAPI = MispAPI()
        plugin_package: str = ""  # TODO: Read config
        enrichment_plugin_factory.load_enrichment_plugins(plugin_package)
        pass

    @property
    def misp_api(self) -> MispAPI:
        return self.__misp_api


enrichment_worker: EnrichmentWorker = EnrichmentWorker()
