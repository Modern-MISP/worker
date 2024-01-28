from mmisp.worker.jobs.enrichment.enrichment_config_data import EnrichmentConfigData
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.misp_database.misp_api import MispAPI


class EnrichmentWorker:
    """
    Encapsulates a Worker for the enrichment jobs.
    The Worker is responsible for managing the configuration and api objects as well as loading the enrichment plugins.
    """

    def __init__(self):
        self.__misp_api: MispAPI = MispAPI()
        self.__config: EnrichmentConfigData
        self.__config = EnrichmentConfigData()
        self.__config.read_config_from_env()

        enrichment_plugin_factory.load_enrichment_plugins(self.__config.plugin_module)

    @property
    def misp_api(self) -> MispAPI:
        """
        The MispAPI object used to communicate with the MISP Backend.
        :return:
        """
        return self.__misp_api

    @property
    def config(self) -> EnrichmentConfigData:
        """
        The configuration for the enrichment jobs.
        """
        return self.__config


enrichment_worker: EnrichmentWorker = EnrichmentWorker()
