import logging
import os
from typing import Self

from pydantic import NonNegativeFloat, ValidationError, constr
from typing_extensions import Annotated

from mmisp.worker.config import ENV_PREFIX, ConfigData

ENV_MISP_API_URL: str = f"{ENV_PREFIX}_DB_API_URL"
ENV_MISP_API_KEY: str = f"{ENV_PREFIX}_DB_API_KEY"
ENV_MISP_API_CONNECT_TIMEOUT: str = f"{ENV_PREFIX}_MISP_API_CONNECT_TIMEOUT"
ENV_MISP_API_READ_TIMEOUT: str = f"{ENV_PREFIX}_MISP_API_READ_TIMEOUT"

_log = logging.getLogger(__name__)


class MispAPIConfigData(ConfigData):
    class Config:
        """
        Pydantic configuration.
        """

        validate_assignment: bool = True

    url: Annotated[str, constr(regex="^https?://\\w")] = "http://127.0.0.1"
    key: str = ""
    connect_timeout: NonNegativeFloat = 40
    read_timeout: NonNegativeFloat = 40

    def __init__(self: Self) -> None:
        super().__init__()
        self.read_from_env()

    def read_from_env(self: Self) -> None:
        """
        Read the environment variables and set the values to the class attributes that are used by the MISP API.
        """

        env_dict: dict = {
            "url": os.environ.get(ENV_MISP_API_URL),
            "key": os.environ.get(ENV_MISP_API_KEY),
            "connect_timeout": os.environ.get(ENV_MISP_API_CONNECT_TIMEOUT),
            "read_timeout": os.environ.get(ENV_MISP_API_READ_TIMEOUT),
        }

        for env in env_dict:
            value: str = env_dict[env]
            if value:
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    _log.warning(f"Could not set {env} to {value}. Error: {validation_error}")


misp_api_config_data: MispAPIConfigData = MispAPIConfigData()
