from pydantic import BaseModel

ENV_PREFIX: str = 'MMISP'
"Prefix for the configuration environment variables."


class ConfigData(BaseModel):
    """
    Base class for configuration data.
    """
    pass
