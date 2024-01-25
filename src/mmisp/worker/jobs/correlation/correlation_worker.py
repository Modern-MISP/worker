from mmisp.worker.jobs.correlation.job_data import ChangeThresholdResponse, ChangeThresholdData
from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
from mmisp.worker.jobs.correlation.correlation_config_data import CorrelationConfigData

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL


class CorrelationWorker:

    MAX_THRESHOLD: int = (2 ** 31) - 1

    def __init__(self):
        self.__misp_api: MispAPI = MispAPI()
        self.__misp_sql: MispSQL = MispSQL()
        self.__config_data: CorrelationConfigData = CorrelationConfigData()
        path: str = ""
        correlation_plugin_factory.load_plugins(path)

    def set_threshold(self, data: ChangeThresholdData) -> ChangeThresholdResponse:
        """
        Setter method to set the new threshold in the configuration data.
        :param data: the new threshold
        :type data: ChangeThresholdData
        :return: if the setting of the threshold was successful, if the threshold was valid and the new threshold
        :rtype: ChangeThresholdResponse
        """
        new_threshold: int = data.new_threshold
        if (new_threshold < 1) or (new_threshold > self.MAX_THRESHOLD):
            return ChangeThresholdResponse(saved=False, valid_threshold=False)
        else:
            self.__config_data.threshold = new_threshold
            return ChangeThresholdResponse(saved=True, valid_threshold=True, new_threshold=new_threshold)

    @property
    def threshold(self) -> int:
        """
        Returns the current threshold in the configuration data.
        :return: the current threshold
        :rtype: int
        """
        return self.__config_data.threshold

    @property
    def misp_api(self) -> MispAPI:
        return self.__misp_api

    @property
    def misp_sql(self) -> MispSQL:
        return self.__misp_sql


correlation_worker = CorrelationWorker()
