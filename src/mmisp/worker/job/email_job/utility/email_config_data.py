from mmisp.worker.config_data import ConfigData


class EmailConfigData(ConfigData):
    misp_url: str
    email_subject_tlp_string: str
    misp_email_address: str
    email_password: str
    smtp_port: int
    smtp_host: str
    """
    Changed from private to public, changed smtpport from string to int
    """