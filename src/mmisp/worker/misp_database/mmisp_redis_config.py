import os

from pydantic import ValidationError

from mmisp.worker.config.config_data import ENV_PREFIX, ConfigData

ENV_REDIS_HOST: str = f"{ENV_PREFIX}_REDIS_HOST"
"""The environment variable name for the Redis host."""
ENV_REDIS_PORT: str = f"{ENV_PREFIX}_REDIS_PORT"
"""The environment variable name for the Redis port."""
ENV_REDIS_DB: str = f"{ENV_PREFIX}_REDIS_DB"
"""The environment variable name for the Redis database name."""
ENV_REDIS_USERNAME: str = f"{ENV_PREFIX}_REDIS_USERNAME"
"""The environment variable name for the Redis username."""
ENV_REDIS_PASSWORD: str = f"{ENV_PREFIX}_REDIS_PASSWORD"
"""The environment variable name for the Redis password."""


class MMispRedisConfigData(ConfigData):
    """
    Encapsulates configuration data for the Redis connection.
    """

    host: str = 'localhost'
    """The host of the Redis database."""
    port: int = 6379
    """The port of the Redis database."""
    db: int = 0
    """The database name of the Redis database."""
    username: str = ''
    """The username of the Redis database."""
    password: str = ''
    """The password of the Redis database."""

    def __init__(self):
        super().__init__()
        self.read_from_env()

    def read_from_env(self):
        """
        Reads the configuration from the environment.
        """

        env_dict: dict = {
            'host': ENV_REDIS_HOST,
            'port': ENV_REDIS_PORT,
            'db': ENV_REDIS_DB,
            'username': ENV_REDIS_USERNAME,
            'password': ENV_REDIS_PASSWORD
        }

        for env in env_dict:
            value: str = os.environ.get(env_dict[env])
            if value:
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    # TODO: Log
                    pass


mmisp_redis_config_data: MMispRedisConfigData = MMispRedisConfigData()
