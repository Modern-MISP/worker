from typing import Self

from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.plugins.plugin_type import PluginType
from mmisp.worker.plugins.factory import PluginFactory


class PluginA:
    PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
        NAME="Dummy Plugin",
        PLUGIN_TYPE=PluginType.ENRICHMENT,
        DESCRIPTION="This is a useless Plugin for demonstration purposes.",
        AUTHOR="Amadeus Haessler",
        VERSION="1.0",
        ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER},
        MISP_ATTRIBUTES=PluginIO(INPUT=["hostname", "domain"], OUTPUT=["ip-src", "ip-dst"]),
    )

    # dummy plugin function not implemented
    def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
        pass

    def run(self: Self) -> EnrichAttributeResult:
        # Plugin logic is implemented here.
        pass


def register(factory: PluginFactory) -> None:
    factory.register(PluginA)
