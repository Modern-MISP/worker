from pydantic import Field, NonNegativeFloat, constr
from pydantic_settings import BaseSettings
from typing_extensions import Annotated

ENV_MISP_API_URL: str = "DB_API_URL"
ENV_MISP_API_KEY: str = "DB_API_KEY"
ENV_MISP_API_CONNECT_TIMEOUT: str = "MISP_API_CONNECT_TIMEOUT"
ENV_MISP_API_READ_TIMEOUT: str = "MISP_API_READ_TIMEOUT"


class MispAPIConfigData(BaseSettings):
    url: Annotated[str, constr(regex="^https?://\\w")] = Field("http://127.0.0.1", env=ENV_MISP_API_URL)
    key: str = Field("", env=ENV_MISP_API_KEY)
    connect_timeout: NonNegativeFloat = Field(40, env=ENV_MISP_API_CONNECT_TIMEOUT)
    read_timeout: NonNegativeFloat = Field(40, env=ENV_MISP_API_READ_TIMEOUT)


misp_api_config_data: MispAPIConfigData = MispAPIConfigData()
