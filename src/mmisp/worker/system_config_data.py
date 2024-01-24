from mmisp.worker.config_data import ConfigData


class SystemConfigData(ConfigData):
    __autostart_correlation_job: bool
    __autostart_email_job: bool
    __autostart_enrichment_job: bool
    __autostart_exception_job: bool
    __autostart_processfreetext_job: bool
    __autostart_pull_job: bool
    __autostart_push_job: bool
