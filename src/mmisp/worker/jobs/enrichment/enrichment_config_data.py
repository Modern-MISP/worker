import logging
import os
from typing import Type

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

ENV_ENRICHMENT_PLUGIN_DIRECTORY = "ENRICHMENT_PLUGIN_DIRECTORY"
"""The name of the environment variable that configures the directory where enrichment plugins are loaded from."""

_PLUGIN_DEFAULT_DIRECTORY: str = ""
"""The default package used for enrichment plugins."""

_log = logging.getLogger(__name__)


class EnrichmentConfigData(BaseSettings):
    """
    Encapsulates configuration for the enrichment worker and its jobs.
    """

    plugin_directory: str = Field(_PLUGIN_DEFAULT_DIRECTORY, validation_alias=ENV_ENRICHMENT_PLUGIN_DIRECTORY)
    """The directory where the plugins are stored."""

    @field_validator("plugin_directory")
    @classmethod
    @classmethod
    def validate_plugin_module(cls: Type["EnrichmentConfigData"], value: str) -> str:
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
                _log.error(f"The given plugin directory {plugin_module} for enrichment plugins does not exist.")

        return _PLUGIN_DEFAULT_DIRECTORY
