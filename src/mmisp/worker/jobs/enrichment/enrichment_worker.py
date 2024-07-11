from typing import Self

from mmisp.worker.jobs.enrichment.enrichment_config_data import EnrichmentConfigData
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.plugins.loader import PluginLoader


class EnrichmentWorker:
    """
    Encapsulates a Worker for the enrichment jobs.
    The Worker is responsible for managing the configuration and api objects as well as loading the enrichment plugins.
    """

    def __init__(self: Self) -> None:
        self.__misp_api: MispAPI = MispAPI()
        self.__config: EnrichmentConfigData = EnrichmentConfigData()
        self.__config.read_config_from_env()

        plugin_path: str = self.__config.plugin_directory
        if plugin_path:
            PluginLoader.load_plugins_from_directory(plugin_path, enrichment_plugin_factory)

    @property
    def misp_api(self: Self) -> MispAPI:
        """
        The MispAPI object used to communicate with the MISP Backend.
        :return: The MispAPI object.
        """
        return self.__misp_api

    @property
    def config(self: Self) -> EnrichmentConfigData:
        """
        The configuration for the enrichment jobs.
        """
        return self.__config


enrichment_worker: EnrichmentWorker = EnrichmentWorker()
