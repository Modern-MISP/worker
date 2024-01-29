import os

from pydantic import NonNegativeInt, StringConstraints, ConfigDict, ValidationError
from typing_extensions import Annotated

from mmisp.worker.config_data import ConfigData, ENV_PREFIX

# TODO: Define ENVs
ENV_MISP_API_URL = f"{ENV_PREFIX}_MISP_API_URL"
ENV_MISP_API_KEY = f"{ENV_PREFIX}_MISP_API_KEY"
ENV_MISP_API_CONNECT_TIMEOUT = f"{ENV_PREFIX}_MISP_API_CONNECT_TIMEOUT"
ENV_MISP_API_READ_TIMEOUT = f"{ENV_PREFIX}_MISP_API_READ_TIMEOUT"


class MispAPIConfigData(ConfigData):
    model_config: ConfigDict = ConfigDict(validate_assignment=True)

    url: Annotated[str, StringConstraints(min_length=8)] = "http://127.0.0.1"  # TODO: Regex (Without trailing slash)
    key: str = ""
    connect_timeout: NonNegativeInt = 40
    read_timeout: NonNegativeInt = 40

    def read_from_env(self):
        env_dict: dict = {
            'url': os.environ.get(ENV_MISP_API_URL),
            'key': os.environ.get(ENV_MISP_API_KEY),
            'connect_timeout': os.environ.get(ENV_MISP_API_CONNECT_TIMEOUT),
            'read_timeout': os.environ.get(ENV_MISP_API_READ_TIMEOUT)
        }

        for env in env_dict:
            value: str = env_dict[env]
            if value:
                try:
                    setattr(self, env, env_dict[env])
                except ValidationError as validation_error:
                    # TODO: Log
                    pass


misp_api_config_data = MispAPIConfigData()
misp_api_config_data.read_from_env()
