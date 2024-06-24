from typing import Self

from mmisp.plugins.enrichment.data import EnrichAttributeResult, NewAttribute
from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.plugins.plugin_type import PluginType


class PassthroughPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
        NAME="Passthrough Plugin",
        PLUGIN_TYPE=PluginType.ENRICHMENT,
        DESCRIPTION="This is a test plugin returning the input unchanged.",
        AUTHOR="Amadeus Haessler",
        VERSION="1.0",
        ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
        MISP_ATTRIBUTES=PluginIO(INPUT=["Any"], OUTPUT=["Any"]),
    )

    def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
        self.__misp_attribute = misp_attribute

    def run(self: Self) -> EnrichAttributeResult:
        return EnrichAttributeResult(attributes=[NewAttribute(attribute=self.__misp_attribute)])
