import logging
import os
from typing import Type

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

ENV_CORRELATION_PLUGIN_DIRECTORY = "CORRELATION_PLUGIN_DIRECTORY"
"""The name of the environment variable that configures the directory where correlation plugins are loaded from."""

PLUGIN_DEFAULT_DIRECTORY: str = ""
"""The default package used for correlation plugins."""

_log = logging.getLogger(__name__)


class CorrelationConfigData(BaseSettings):
    """
    Encapsulates configuration for the correlation worker and its jobs.
    """

    plugin_directory: str = Field(PLUGIN_DEFAULT_DIRECTORY, validation_alias=ENV_CORRELATION_PLUGIN_DIRECTORY)
    """The directory where the plugins are stored."""

    @field_validator("plugin_directory")
    @classmethod
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
