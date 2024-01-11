from src.plugins.factory import PluginFactory
from src.plugins.plugin import PluginType, PluginInfo
from src.job.enrichment_job.job_data import EnrichAttributeResult
from src.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO


class DummyPlugin:
    PLUGIN_INFO: PluginInfo = PluginInfo(NAME='dk', PLUGIN_TYPE=PluginType.ENRICHMENT,
                                         DESCRIPTION='Descriptionjdafja', AUTHOR='Amadeus Haessler', VERSION=1.0,
                                         ENRICHMENT_TYPE={EnrichmentPluginType.EXPANSION, EnrichmentPluginType.HOVER},
                                         MISP_ATTRIBUTE=PluginIO(INPUT=['hostname', 'domain'],
                                                                 OUTPUT=['ip-src', 'ip-dst'])
                                         )

    def run(self) -> EnrichAttributeResult:
        pass


def register(factory: PluginFactory):
    factory.register(DummyPlugin.PLUGIN_INFO.NAME, DummyPlugin)
