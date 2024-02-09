import os

from pydantic import ValidationError, NonNegativeInt

from mmisp.worker.config.config_data import ConfigData, ENV_PREFIX

ENV_MISP_URL = f"{ENV_PREFIX}_MISP_URL"
ENV_EMAIL_SUBJECT_STRING = f"{ENV_PREFIX}_EMAIL_SUBJECT_STRING"
ENV_MISP_EMAIL_ADDRESS = f"{ENV_PREFIX}_MISP_EMAIL_ADDRESS"
ENV_EMAIL_PASSWORD = f"{ENV_PREFIX}_EMAIL_PASSWORD"
ENV_SMTP_PORT = f"{ENV_PREFIX}_SMTP_PORT"
ENV_SMTP_HOST = f"{ENV_PREFIX}_SMTP_HOST"


class EmailConfigData(ConfigData):
    """
    Encapsulates configuration for the email worker and its jobs.
    """

    misp_url: str = "http://127.0.0.1"
    """The url of MISP"""
    email_subject_string: str = "TLP: "
    """The tlp string to search for an email subject"""
    misp_email_address: str = "misp@localhost"
    """The email of MISP"""
    misp_email_password: str = ""
    """The password of the MISP email"""
    smtp_port: NonNegativeInt = 25
    """The port of the SMTP server"""
    smtp_host: str = "localhost"
    """The host of the SMTP server"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_from_env()

    def read_from_env(self):
        """
        Reads the configuration from the environment.
        """

        env_dict: dict = {
            'misp_url': os.environ.get(ENV_MISP_URL),
            'email_subject_string': os.environ.get(ENV_EMAIL_SUBJECT_STRING),
            'misp_email_address': os.environ.get(ENV_MISP_EMAIL_ADDRESS),
            'misp_email_password': os.environ.get(ENV_EMAIL_PASSWORD),
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
