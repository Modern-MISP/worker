from src.job.config_data import ConfigData


class PullConfigData(ConfigData):
    def __init__(self):
        super().__init__()
        self.__misp_enable_event_blocklisting: bool
        self.__misp_enable_org_blocklisting: bool
        self.current_user_id: int
        self.__misp_host_org_id: int
        self.__misp_enable_synchronisation_filtering_on_type: bool
