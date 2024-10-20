import logging
import os
from typing import Self

from pydantic import NonNegativeInt, ValidationError

from mmisp.worker.config import ENV_PREFIX, ConfigData

ENV_URL = f"{ENV_PREFIX}_URL"
ENV_EMAIL_SUBJECT_STRING = f"{ENV_PREFIX}_EMAIL_SUBJECT_STRING"
ENV_EMAIL_ADDRESS = f"{ENV_PREFIX}_EMAIL_ADDRESS"
ENV_EMAIL_USERNAME = f"{ENV_PREFIX}_EMAIL_USERNAME"
ENV_EMAIL_PASSWORD = f"{ENV_PREFIX}_EMAIL_PASSWORD"
ENV_SMTP_PORT = f"{ENV_PREFIX}_SMTP_PORT"
ENV_SMTP_HOST = f"{ENV_PREFIX}_SMTP_HOST"

_log = logging.getLogger(__name__)


class EmailConfigData(ConfigData):
    """
    Encapsulates configuration for the email worker and its jobs.
    """

    mmisp_url: str = "http://127.0.0.1"
    """The url of MISP"""
    email_subject_string: str = "tlp"
    """The tlp string to search for an email subject"""
    mmisp_email_address: str = "misp@localhost"
    """The email of MISP"""
    mmisp_email_username: str = "misp"
    """The username of the MISP email"""
    mmisp_email_password: str = ""
    """The password of the MISP email"""
    mmisp_smtp_port: NonNegativeInt = 25
    """The port of the SMTP server"""
    mmisp_smtp_host: str = "localhost"
    """The host of the SMTP server"""

    def __init__(self: Self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.read_from_env()

    def read_from_env(self: Self) -> None:
        """
        Reads the configuration from the environment.
        """

        env_dict: dict = {
            "mmisp_url": os.environ.get(ENV_URL),
            "email_subject_string": os.environ.get(ENV_EMAIL_SUBJECT_STRING),
            "mmisp_email_address": os.environ.get(ENV_EMAIL_ADDRESS),
            "mmisp_email_username": os.environ.get(ENV_EMAIL_USERNAME),
            "mmisp_email_password": os.environ.get(ENV_EMAIL_PASSWORD, ""),
            "mmisp_smtp_port": os.environ.get(ENV_SMTP_PORT),
            "mmisp_smtp_host": os.environ.get(ENV_SMTP_HOST),
        }

        for env in env_dict:
            value: str = env_dict[env]
            if value:
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    _log.exception(f"Error while reading {env} from environment: {validation_error}")
