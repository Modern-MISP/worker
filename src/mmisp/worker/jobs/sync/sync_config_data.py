from mmisp.worker.config_data import ConfigData


class SyncConfigData(ConfigData):
    misp_enable_event_blocklisting: bool
    misp_enable_org_blocklisting: bool
    current_user_id: int
    misp_host_org_id: int
    misp_enable_synchronisation_filtering_on_type: bool

sync_config_data: SyncConfigData = SyncConfigData()