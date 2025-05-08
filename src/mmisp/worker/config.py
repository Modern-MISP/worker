from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class SystemConfigData(BaseSettings):
    """
    Encapsulates the general configuration of the MMISP Worker application.
    """

    api_port: PositiveInt = Field(5000, validation_alias="API_PORT")
    """The port exposing the API."""

    api_key: str = Field(validation_alias="API_KEY")
    """The key for the API."""

    api_host: str = Field("0.0.0.0", validation_alias="API_HOST")
    """The host the API binds to."""

    worker_termination_timeout: int = 30
    """The time in seconds to wait for the worker to terminate before kill."""

    worker_api_key: str = Field(validation_alias="WORKER_API_KEY")


system_config_data = SystemConfigData()
