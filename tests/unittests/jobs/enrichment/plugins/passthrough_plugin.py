from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginInfo, EnrichmentPluginType, PluginIO
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.plugins.plugin import PluginType


class PassthroughPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = (
        EnrichmentPluginInfo(NAME="Passthrough Plugin",
                             PLUGIN_TYPE=PluginType.ENRICHMENT,
                             DESCRIPTION="This is a test plugin returning the input unchanged.",
                             AUTHOR="Amadeus Haessler", VERSION="1.0",
                             ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION},
                             MISP_ATTRIBUTES=PluginIO(INPUT=['Any'],
                                                      OUTPUT=['Any'])
                             ))

    def __init__(self, misp_attribute: MispEventAttribute):
        self.__misp_attribute = misp_attribute

    def run(self) -> EnrichAttributeResult:
        return EnrichAttributeResult(attributes=[self.__misp_attribute])
