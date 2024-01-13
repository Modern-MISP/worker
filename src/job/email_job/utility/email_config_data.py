from src.job.config_data import ConfigData


class EmailConfigData(ConfigData):

    __misp_url: str
    __misp_email_address: str
    __smtp_port: str
    __smtp_host: str
    __email_password: str
    __email_subject_tlp_string: str

    def load_config(self):
        pass
