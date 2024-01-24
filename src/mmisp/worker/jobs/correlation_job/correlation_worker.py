from mmisp.worker.job.correlation_job.job_data import ChangeThresholdResponse, ChangeThresholdData
from mmisp.worker.job.correlation_job.plugins.correlation_plugin_info import CorrelationPluginInfo
from mmisp.worker.job.correlation_job.plugins.correlation_plugin_factory import CorrelationPluginFactory
from mmisp.worker.job.correlation_job.correlation_config_data import CorrelationConfigData


class CorrelationWorker:

    MAX_THRESHOLD: int = (2 ** 31) - 1

    __plugin_factory: CorrelationPluginFactory()
    __config_data: CorrelationConfigData()
    __threshold: int

    @classmethod
    def load_correlation_plugins(cls):
        pass

    @classmethod
    def set_threshold(cls, data: ChangeThresholdData) -> ChangeThresholdResponse:
        new_threshold: int = ChangeThresholdData.new_threshold
        if (new_threshold < 1) or (new_threshold > cls.MAX_THRESHOLD):
            return ChangeThresholdResponse(saved=False, valid_threshold=False)
        else:
            cls.__threshold = new_threshold
            # TODO change config data
            return ChangeThresholdResponse(saved=True, valid_threshold=True, new_threshold=new_threshold)

    @classmethod
    def get_threshold(cls) -> int:
        return cls.__threshold

    @classmethod
    def get_plugin_factory(cls) -> CorrelationPluginFactory:
        return cls.__plugin_factory

    @classmethod
    def get_plugins(cls) -> list[CorrelationPluginInfo]:
        pass

    @classmethod
    def set_correlation_config_data(cls, config_data: CorrelationConfigData) -> bool:
        CorrelationWorker.__config_data = config_data
        return True
