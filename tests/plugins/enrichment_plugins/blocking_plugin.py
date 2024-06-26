from time import sleep

from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.plugins.factory import PluginFactory
from mmisp.worker.plugins.plugin import PluginType

EXAMPLE_ATTRIBUTE: MispEventAttribute = MispEventAttribute(event_id=1, object_id=0, category="Other",
                                                           type="other", distribution=0, value="Test"
                                                           )


class BlockingPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = (
        EnrichmentPluginInfo(NAME="Blocking Plugin",
                             PLUGIN_TYPE=PluginType.ENRICHMENT,
                             DESCRIPTION="The plugin blocks the job "
                                         "for a certain amount of time "
                                         "without doing anything else.",
                             AUTHOR="Amadeus Haessler", VERSION="1.0",
                             ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION,
                                              EnrichmentPluginType.HOVER},
                             MISP_ATTRIBUTES=PluginIO(
                                 INPUT=['other'],
                                 OUTPUT=['other'])))

    # dummy plugin function not implemented
    def __init__(self, misp_attribute: MispEventAttribute):
        pass

    def run(self) -> EnrichAttributeResult:
        sleep(5)
        return EnrichAttributeResult()


def register(factory: PluginFactory):
    factory.register(BlockingPlugin)
