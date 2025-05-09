from typing import Annotated, Self

from pydantic import Field, field_validator
from pydantic.networks import WebsocketUrl
from pydantic_settings import BaseSettings, NoDecode


class NodeConfig(BaseSettings):
    worker_api_url: WebsocketUrl = Field(validation_alias="WORKER_API_WEBSOCKET")
    worker_api_key: str = Field(validation_alias="WORKER_API_KEY")

    enrichment_plugin_dir: Annotated[list[str] | None, NoDecode] = Field(None, validation_alias="ENRICHMENT_PLUGIN_DIR")
    correlation_plugin_dir: Annotated[list[str] | None, NoDecode] = Field(
        None, validation_alias="CORRELATION_PLUGIN_DIR"
    )

    workers: Annotated[list[str], NoDecode] = Field("ALL", validation_alias="WORKERS")  # type: ignore
    """List of workers to start automatically"""

    @field_validator("workers", "enrichment_plugin_dir", "correlation_plugin_dir", mode="before")
    @classmethod
    def split_on_comma(cls: type[Self], v: str | None) -> list[str] | None:
        if v is None:
            return None
        return [x for x in v.split(",")]


node_config = NodeConfig()
