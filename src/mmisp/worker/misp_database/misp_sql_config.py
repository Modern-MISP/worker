import logging
import os
from typing import Self, Type

from pydantic import ConfigDict, PositiveInt, ValidationError, constr, validator

from mmisp.worker.config.config_data import ENV_PREFIX, ConfigData

ENV_MISP_SQL_DBMS: str = f"{ENV_PREFIX}_DB_SQL_DBMS"
"""The environment variable name for the MISP database DBMS."""
ENV_MISP_SQL_HOST: str = f"{ENV_PREFIX}_DB_SQL_HOST"
"""The environment variable name for the MISP database host."""
ENV_MISP_SQL_PORT: str = f"{ENV_PREFIX}_DB_SQL_PORT"
"""The environment variable name for the MISP database port."""
ENV_MISP_SQL_USER: str = f"{ENV_PREFIX}_DB_SQL_USER"
"""The environment variable name for the MISP database user."""
ENV_MISP_SQL_PASSWORD: str = f"{ENV_PREFIX}_DB_SQL_PASSWORD"
"""The environment variable name for the MISP database password."""
ENV_MISP_SQL_DATABASE: str = f"{ENV_PREFIX}_DB_SQL_DATABASE"
"""The environment variable name for the MISP database name."""

ALLOWED_DBMS: list[str] = [
    "mysql",
    "mariadb",
    # 'postgresql',
]
"""The allowed DBMS for the MISP database."""

_log = logging.getLogger(__name__)


class MispSQLConfigData(ConfigData):
    """
    Encapsulates configuration data for the Misp database connection.
    """

    model_config: ConfigDict = ConfigDict(validate_assignment=True, str_strip_whitespace=True, str_min_length=1)

    dbms: str = "mysql"
    """The DBMS of the MISP SQL database."""
    host: str = "localhost"
    """The host of the MISP SQL database."""
    port: PositiveInt = 3306
    """The port of the MISP SQL database."""
    user: str = "mmisp"
    """The user of the MISP SQL database."""
    password: constr(min_length=0) = ""
    """The password of the MISP SQL database."""
    database: str = "misp"
    """The database name of the MISP SQL database."""

    def __init__(self: Self) -> None:
        super().__init__()
        self.read_from_env()

    @validator("dbms")
    @classmethod
    def validate_dbms(cls: Type["MispSQLConfigData"], value: str) -> str:
        """
        Validates the DBMS value.
        """

        if value and value in ALLOWED_DBMS:
            return value
        else:
            raise ValueError(f"'{ENV_MISP_SQL_DBMS}' must be one of '{ALLOWED_DBMS}', but was '{value}'.")

    def read_from_env(self: Self) -> None:
        """
        Reads the configuration from the environment.
        """

        env_dict: dict = {
            "dbms": os.environ.get(ENV_MISP_SQL_DBMS),
            "host": os.environ.get(ENV_MISP_SQL_HOST),
            "port": os.environ.get(ENV_MISP_SQL_PORT),
            "user": os.environ.get(ENV_MISP_SQL_USER),
            "password": os.environ.get(ENV_MISP_SQL_PASSWORD),
            "database": os.environ.get(ENV_MISP_SQL_DATABASE),
        }

        for env in env_dict.keys():
            value: str = env_dict[env]
            if value:
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    _log.exception(
                        f"{env_dict[env]}: Could not set value from environment variable. {validation_error}"
                    )


misp_sql_config_data: MispSQLConfigData = MispSQLConfigData()
