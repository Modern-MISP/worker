from src.mmisp.worker.plugins.factory import PluginFactory
from src.mmisp.worker.plugins.plugin import PluginType, PluginInfo
from src.mmisp.worker.jobs.enrichment.job_data import EnrichAttributeResult
from src.mmisp.worker.jobs.enrichment.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO, \
    EnrichmentPluginInfo


class DummyPlugin:
    PLUGIN_INFO: EnrichmentPluginInfo = PluginInfo(NAME="Dummy Plugin", PLUGIN_TYPE=PluginType.ENRICHMENT,
                                                   DESCRIPTION="This is a useless Plugin for demonstration purposes.",
                                                   AUTHOR="Amadeus Haessler", VERSION=1.0,
                                                   ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION,
                                                                    EnrichmentPluginType.HOVER},
                                                   MISP_ATTRIBUTE=PluginIO(INPUT=['hostname', 'domain'],
                                                                           OUTPUT=['ip-src', 'ip-dst']))

    def run(self) -> EnrichAttributeResult:
        # Plugin logic is implemented here.
        pass


def register(factory: PluginFactory):
    factory.register(DummyPlugin.PLUGIN_INFO.NAME, DummyPlugin)


