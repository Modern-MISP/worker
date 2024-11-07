from time import sleep
from typing import Self

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.enrichment.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.plugins.models.attribute import AttributeWithTagRelationship
from mmisp.plugins.plugin_type import PluginType
from mmisp.worker.plugins.factory import PluginFactory

EXAMPLE_ATTRIBUTE: AddAttributeBody = AddAttributeBody(
    event_id=1, object_id=0, category="Other", type="other", distribution=0, value="Test"
)


class BlockingPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = EnrichmentPluginInfo(
        NAME="Blocking Plugin",
        PLUGIN_TYPE=PluginType.ENRICHMENT,
        DESCRIPTION="The plugin blocks the job for a certain amount of time without doing anything else.",
        AUTHOR="Amadeus Haessler",
        VERSION="1.0",
        ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER},
        MISP_ATTRIBUTES=PluginIO(INPUT=["other"], OUTPUT=["other"]),
    )

    def __init__(self: Self, misp_attribute: AttributeWithTagRelationship) -> None:
        # dummy plugin function not implemented
        pass

    def run(self: Self) -> EnrichAttributeResult:
        sleep(5)
        return EnrichAttributeResult()


def register(factory: PluginFactory):
    factory.register(BlockingPlugin)
