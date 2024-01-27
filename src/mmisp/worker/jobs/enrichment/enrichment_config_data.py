import importlib.util
import os

from pydantic import field_validator, ConfigDict

from mmisp.worker.config_data import ConfigData, ENV_PREFIX

ENV_ENRICHMENT_PLUGIN_MODULE = f"{ENV_PREFIX}_ENRICHMENT_PLUGIN_MODULE"
"""The name of the environment variable that configures the python package where enrichment plugins are loaded from."""

PLUGIN_DEFAULT_PACKAGE: str = 'plugins.enrichment_plugins'
"""The default package used for enrichment plugins."""


class EnrichmentConfigData(ConfigData):
    """
    Encapsulates configuration for the enrichment worker and its jobs.
    """

    model_config = ConfigDict(validate_assignment=True)

    plugin_module: str = PLUGIN_DEFAULT_PACKAGE
    """The module where the plugins are stored."""

    @field_validator('plugin_module')
    @classmethod
    def validate_plugin_module(cls, value) -> str:
        """
        Validates the plugin_module.
        If the module is not valid or could not be found a default value is assigned.
        :param value: The plugin_module value.
        :type value: str
        :return: The given or a default plugin module.
        """

        plugin_module: str = value.strip()

        if plugin_module:
            if importlib.util.find_spec(plugin_module):
                return plugin_module
            else:
                # TODO: Log Error
                pass

        return PLUGIN_DEFAULT_PACKAGE

    def read_config_from_env(self):
        """
        Reads the configuration of the enrichment worker from environment variables.
        """
        plugin_module: str = os.environ.get(ENV_ENRICHMENT_PLUGIN_MODULE)
        self.plugin_module = plugin_module
