from pydantic import Field, NonNegativeFloat
from pydantic_settings import BaseSettings

ENV_MISP_API_URL: str = "DB_API_URL"
ENV_MISP_API_KEY: str = "DB_API_KEY"
ENV_MISP_API_CONNECT_TIMEOUT: str = "MISP_API_CONNECT_TIMEOUT"
ENV_MISP_API_READ_TIMEOUT: str = "MISP_API_READ_TIMEOUT"


class MispAPIConfigData(BaseSettings):
    url: str = Field("http://127.0.0.1", pattern="^https?://\\w", validation_alias=ENV_MISP_API_URL)
    key: str = Field("", validation_alias=ENV_MISP_API_KEY)
    connect_timeout: NonNegativeFloat = Field(40, validation_alias=ENV_MISP_API_CONNECT_TIMEOUT)
    read_timeout: NonNegativeFloat = Field(40, validation_alias=ENV_MISP_API_READ_TIMEOUT)


misp_api_config_data: MispAPIConfigData = MispAPIConfigData()
