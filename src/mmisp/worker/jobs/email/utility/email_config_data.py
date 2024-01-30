from mmisp.worker.config_data import ConfigData


class EmailConfigData(ConfigData):
    """
    Encapsulates configuration for the email worker and its jobs.
    """
    misp_url: str
    """The url of MISP"""
    email_subject_tlp_string: str
    """The tlp string to search for an email subject"""
    misp_email_address: str
    """The email of MISP"""
    email_password: str
    """The password of the MISP email"""
    smtp_port: int
    """The port of the SMTP server"""
    smtp_host: str
    """The host of the SMTP server"""
