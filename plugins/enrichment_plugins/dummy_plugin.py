from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO, \
    EnrichmentPluginInfo
from mmisp.worker.plugins.factory import PluginFactory
from mmisp.worker.plugins.plugin import PluginType


class DummyPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = (
        EnrichmentPluginInfo(NAME="Dummy Plugin", PLUGIN_TYPE=PluginType.ENRICHMENT,
                             DESCRIPTION="This is a useless Plugin for demonstration purposes.",
                             AUTHOR="Amadeus Haessler", VERSION="1.0",
                             ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER},
                             MISP_ATTRIBUTES=PluginIO(INPUT=['hostname', 'domain'],
                                                     OUTPUT=['ip-src', 'ip-dst'])))

    # dummy plugin function not implemented
    def __init__(self, misp_attribute: MispEventAttribute):
        pass

    def run(self) -> EnrichAttributeResult:
        # Plugin logic is implemented here.
        pass


def register(factory: PluginFactory):
    factory.register(DummyPlugin)
