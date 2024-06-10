import logging
import os

from pydantic import ConfigDict, validator

from mmisp.worker.config.config_data import ConfigData, ENV_PREFIX

ENV_ENRICHMENT_PLUGIN_DIRECTORY = f"{ENV_PREFIX}_ENRICHMENT_PLUGIN_DIRECTORY"
"""The name of the environment variable that configures the directory where enrichment plugins are loaded from."""

_PLUGIN_DEFAULT_DIRECTORY: str = ''
"""The default package used for enrichment plugins."""

_log = logging.getLogger(__name__)


class EnrichmentConfigData(ConfigData):
    """
    Encapsulates configuration for the enrichment worker and its jobs.
    """

    model_config = ConfigDict(validate_assignment=True)

    plugin_directory: str = _PLUGIN_DEFAULT_DIRECTORY
    """The directory where the plugins are stored."""

    @validator('plugin_directory')
    @classmethod
    def validate_plugin_module(cls, value) -> str:
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

    def read_config_from_env(self):
        """
        Reads the configuration of the enrichment worker from environment variables.
        """
        env = os.environ.get(ENV_ENRICHMENT_PLUGIN_DIRECTORY)
        if env:
            plugin_directory: str = env
            self.plugin_directory = plugin_directory
