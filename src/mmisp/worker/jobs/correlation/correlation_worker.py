from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.jobs.correlation.job_data import ChangeThresholdResponse, ChangeThresholdData
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.correlation_config_data import CorrelationConfigData

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.plugins.loader import PluginLoader
import logging

log = logging.getLogger(__name__)


class CorrelationWorker:

    MAX_THRESHOLD: int = (2 ** 31) - 1

    def __init__(self):
        self.__threshold: int = 20
        self.__misp_api: MispAPI = MispAPI()
        self.__misp_sql: MispSQL = MispSQL()
        self.__config_data: CorrelationConfigData = CorrelationConfigData()
        self.__config_data.read_config_from_env()

        plugin_path: str = self.__config_data.plugin_directory
        if plugin_path:
            PluginLoader.load_plugins_from_directory(plugin_path, correlation_plugin_factory)

    def set_threshold(self, user: UserData, data: ChangeThresholdData) -> ChangeThresholdResponse:
        """
        Setter method to set the new threshold in the configuration data.
        :param user: the user who wants to change the threshold
        :type user: UserData
        :param data: the new threshold
        :type data: ChangeThresholdData
        :return: if the setting of the threshold was successful, if the threshold was valid and the new threshold
        :rtype: ChangeThresholdResponse
        """

        new_threshold: int = data.new_threshold
        if (new_threshold < 1) or (new_threshold > self.MAX_THRESHOLD):
            return ChangeThresholdResponse(saved=False, valid_threshold=False)
        else:
            self.__threshold = new_threshold
            log.info(f"User {user.user_id} changed the threshold form {self.threshold} to {data.new_threshold}.")
            return ChangeThresholdResponse(saved=True, valid_threshold=True, new_threshold=new_threshold)

    @property
    def threshold(self) -> int:
        """
        Returns the current threshold.
        :return: the current threshold
        :rtype: int
        """
        return self.__threshold

    @property
    def misp_api(self) -> MispAPI:
        """
        Getter method to get the misp api.
        :return: the misp api
        :rtype: MispAPI
        """
        return self.__misp_api

    @property
    def misp_sql(self) -> MispSQL:
        """
        Getter method to get the misp sql.
        :return: the misp sql
        :rtype: MispSQL
        """
        return self.__misp_sql


correlation_worker = CorrelationWorker()
