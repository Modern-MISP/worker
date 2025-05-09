from typing import Self

from pydantic import Field
from pydantic_settings import BaseSettings


class RedisConfigData(BaseSettings):
    """
    Encapsulates configuration data for the Redis connection.
    """

    host: str = Field("localhost", validation_alias="REDIS_HOST")
    """The host of the Redis database."""
    port: int = Field(6379, validation_alias="REDIS_PORT")
    """The port of the Redis database."""
    db: int = Field(0, validation_alias="REDIS_DB")
    """The database name of the Redis database."""
    username: str = Field("", validation_alias="REDIS_USERNAME")
    """The username of the Redis database."""
    password: str = Field("", validation_alias="REDIS_PASSWORD")
    """The password of the Redis database."""

    def redis_url(self: Self) -> str:
        """
        Formats the Redis configuration as a URL string.
        """
        auth_part = ""
        if self.username and self.password:
            auth_part = f"{self.username}:{self.password}@"
        elif self.password:
            auth_part = f":{self.password}@"

        return f"redis://{auth_part}{self.host}:{self.port}/{self.db}"


redis_config = RedisConfigData()
