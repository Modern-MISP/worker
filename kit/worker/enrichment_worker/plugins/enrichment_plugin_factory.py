from typing import List

from kit.misp_dataclasses.misp_attribute import MispEventAttribute
from kit.misp_dataclasses.misp_tag import MispTag
from kit.plugins.factory import PluginFactory
from kit.worker.enrichment_worker.plugins.enrichment_plugin import EnrichmentPlugin


class EnrichmentPluginFactory(PluginFactory[EnrichmentPlugin]):

    def create(self, plugin_name: str, misp_attribute: MispEventAttribute, misp_attribute_tags: List[MispTag]) \
            -> EnrichmentPlugin:
        """
        Create an instance of a plugin.

        :param plugin_name: The name of the plugin.
        :type plugin_name: str
        :param misp_attribute: The MISP-Attribute to enrich.
        :type misp_attribute: MispEventAttribute
        :param misp_attribute_tags: MISP-Tags attached to the MISP-Attribute.
        :type misp_attribute_tags: List[MispTag]
        :return: The instantiated enrichment plugin, initialized with the MISP-Attribute and relating tags.
        """

        pass
        # try:
        #    creator_func = self.plugin_creation_funcs[plugin_name]
        # except KeyError:
        #    raise ValueError(f"TODO") from None
        # return creator_func(misp_attribute, misp_attribute_tags)

    def get_enrichment_plugins(self) -> List[EnrichmentPlugin]:
        pass
