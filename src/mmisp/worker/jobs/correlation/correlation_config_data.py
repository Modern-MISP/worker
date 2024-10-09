import logging
import os
from typing import Self, Type

from pydantic import validator

from mmisp.worker.config import ENV_PREFIX, ConfigData

ENV_CORRELATION_PLUGIN_DIRECTORY = f"{ENV_PREFIX}_CORRELATION_PLUGIN_DIRECTORY"
"""The name of the environment variable that configures the directory where correlation plugins are loaded from."""

PLUGIN_DEFAULT_DIRECTORY: str = ""
"""The default package used for correlation plugins."""

_log = logging.getLogger(__name__)


class CorrelationConfigData(ConfigData):
    """
    Encapsulates configuration for the correlation worker and its jobs.
    """

    class Config:
        """
        Pydantic configuration.
        """

        validate_assignment: bool = True

    plugin_directory: str = PLUGIN_DEFAULT_DIRECTORY
    """The directory where the plugins are stored."""

    @validator("plugin_directory")
    @classmethod
    def validate_plugin_module(cls: Type["CorrelationConfigData"], value: str) -> str:
        """
        Validates the plugin_directory.
        If the module is not valid or could not be found a default value is assigned.
        :param value: The plugin_directory value.
        :type value: str
        :return: The given or a default plugin directory.
        """

        plugin_module: str = value.strip()

        if plugin_module:
            if os.path.isdir(plugin_module):
                return plugin_module
            else:
                _log.error(f"The given plugin directory '{plugin_module}' for correlation plugins does not exist.")

        return PLUGIN_DEFAULT_DIRECTORY

    def read_config_from_env(self: Self) -> None:
        """
        Reads the configuration of the correlation worker from environment variables.
        """
        env_plugin = os.environ.get(ENV_CORRELATION_PLUGIN_DIRECTORY)
        if env_plugin:
            self.plugin_directory = env_plugin
