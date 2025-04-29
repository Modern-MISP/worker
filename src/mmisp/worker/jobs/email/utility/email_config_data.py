from pydantic import Field, NonNegativeInt
from pydantic_settings import BaseSettings

ENV_URL = "URL"
ENV_EMAIL_SUBJECT_STRING = "EMAIL_SUBJECT_STRING"
ENV_EMAIL_ADDRESS = "EMAIL_ADDRESS"
ENV_EMAIL_USERNAME = "EMAIL_USERNAME"
ENV_EMAIL_PASSWORD = "EMAIL_PASSWORD"
ENV_SMTP_PORT = "SMTP_PORT"
ENV_SMTP_HOST = "SMTP_HOST"


class EmailConfigData(BaseSettings):
    """
    Encapsulates configuration for the email worker and its jobs.
    """

    mmisp_url: str = Field("http://127.0.0.1", validation_alias=ENV_URL)
    """The url of MISP"""
    email_subject_string: str = Field("tlp", validation_alias=ENV_EMAIL_SUBJECT_STRING)
    """The tlp string to search for an email subject"""
    mmisp_email_address: str = Field("misp@localhost", validation_alias=ENV_EMAIL_ADDRESS)
    """The email of MISP"""
    mmisp_email_username: str = Field("misp", validation_alias=ENV_EMAIL_USERNAME)
    """The username of the MISP email"""
    mmisp_email_password: str = Field("", validation_alias=ENV_EMAIL_PASSWORD)
    """The password of the MISP email"""
    mmisp_smtp_port: NonNegativeInt = Field(25, validation_alias=ENV_SMTP_PORT)
    """The port of the SMTP server"""
    mmisp_smtp_host: str = Field("localhost", validation_alias=ENV_SMTP_HOST)
    """The host of the SMTP server"""
