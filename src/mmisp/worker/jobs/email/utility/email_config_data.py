import os

from pydantic import ValidationError

from mmisp.worker.config.config_data import ConfigData, ENV_PREFIX

ENV_MISP_URL = f"{ENV_PREFIX}_MISP_URL"
ENV_EMAIL_SUBJECT_TLP_STRING = f"{ENV_PREFIX}_EMAIL_SUBJECT_TLP_STRING"
ENV_MISP_EMAIL_ADDRESS = f"{ENV_PREFIX}_MISP_EMAIL_ADDRESS"
ENV_EMAIL_PASSWORD = f"{ENV_PREFIX}_EMAIL_PASSWORD"
ENV_SMTP_PORT = f"{ENV_PREFIX}_SMTP_PORT"
ENV_SMTP_HOST = f"{ENV_PREFIX}_SMTP_HOST"


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

    def __init__(self):
        super().__init__()
        self.read_from_env()

    def read_from_env(self):
        """
        Reads the configuration from the environment.
        """

        env_dict: dict = {
            'misp_url': os.environ.get(ENV_MISP_URL),
            'email_subject_tlp_string': os.environ.get(ENV_EMAIL_SUBJECT_TLP_STRING),
            'misp_email_address': os.environ.get(ENV_MISP_EMAIL_ADDRESS),
            'email_password': os.environ.get(ENV_EMAIL_PASSWORD),
            'smtp_port': os.environ.get(ENV_SMTP_PORT),
            'smtp_host': os.environ.get(ENV_SMTP_HOST)
        }

        for env in env_dict:
            value: str = env_dict[env]
            if value:
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    # TODO: Log ENV Error
                    pass


email_config_data = EmailConfigData()
