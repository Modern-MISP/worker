from mmisp.worker.config.config_data import ConfigData


class PullConfigData(ConfigData):
    """
    TODO: Default values / Initialization
    """

    misp_enable_event_blocklisting: bool
    misp_enable_org_blocklisting: bool
    current_user_id: int
    misp_host_org_id: int
    misp_enable_synchronisation_filtering_on_type: bool


sync_config_data: PullConfigData = PullConfigData(misp_enable_event_blocklisting=False,
                                                  misp_enable_org_blocklisting=False,
                                                  current_user_id=0,
                                                  misp_host_org_id=0,
                                                  misp_enable_synchronisation_filtering_on_type=False)
