import os

from pydantic import ValidationError, ConfigDict, field_validator, PositiveInt, StringConstraints
from typing_extensions import Annotated

from mmisp.worker.config_data import ConfigData, ENV_PREFIX

ENV_MISP_SQL_DBMS: str = f"{ENV_PREFIX}_MISP_SQL_DBMS"
ENV_MISP_SQL_HOST: str = f"{ENV_PREFIX}_MISP_SQL_HOST"
ENV_MISP_SQL_PORT: str = f"{ENV_PREFIX}_MISP_SQL_PORT"
ENV_MISP_SQL_USER: str = f"{ENV_PREFIX}_MISP_SQL_USER"
ENV_MISP_SQL_PASSWORD: str = f"{ENV_PREFIX}_MISP_SQL_PASSWORD"
ENV_MISP_SQL_DATABASE: str = f"{ENV_PREFIX}_MISP_SQL_DATABASE"

ALLOWED_DBMS: list[str] = ['mysql', 'mariadb', 'postgresql']


class MispSQLConfigData(ConfigData):
    model_config: ConfigDict = ConfigDict(validate_assignment=True, str_strip_whitespace=True, str_min_length=1)

    dbms: str = 'mysql'
    """The DBMS of the MISP SQL database."""
    host: str = 'localhost'
    """The host of the MISP SQL database."""
    port: PositiveInt = 3306
    """The port of the MISP SQL database."""
    user: str = 'mmisp'
    """The user of the MISP SQL database."""
    password: Annotated[str, StringConstraints(min_length=0)] = ''
    """The password of the MISP SQL database."""
    database: str = 'misp'
    """The database name of the MISP SQL database."""

    @field_validator('dbms')
    @classmethod
    def validate_dbms(cls, value) -> str:

        if value and value in ALLOWED_DBMS:
            return value
        else:
            raise ValueError(f"'{ENV_MISP_SQL_DBMS}' must be one of '{ALLOWED_DBMS}', but was '{value}'.")

    def read_from_env(self):
        env_dict: dict = {
            'dbms': os.environ.get(ENV_MISP_SQL_DBMS),
            'host': os.environ.get(ENV_MISP_SQL_HOST),
            'port': os.environ.get(ENV_MISP_SQL_PORT),
            'user': os.environ.get(ENV_MISP_SQL_USER),
            'password': os.environ.get(ENV_MISP_SQL_PASSWORD),
            'database': os.environ.get(ENV_MISP_SQL_DATABASE)
        }

        for env in env_dict.keys():
            value: str = env_dict[env]
            if value:
                try:
                    setattr(self, env, value)
                except ValidationError as validation_error:
                    # TODO: Log
                    pass


misp_sql_config_data = MispSQLConfigData()
misp_sql_config_data.read_from_env()
