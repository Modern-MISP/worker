from src.plugins.factory import PluginFactory
from src.plugins.plugin import PluginType, PluginMeta
from src.job.enrichment_job.job_data import EnrichAttributeResult
from src.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO


class DummyPlugin:
    PLUGIN_META: PluginMeta = PluginMeta(name='dk', pluginType=PluginType.ENRICHMENT,
                                         description='Descriptionjdafja', author='Amadeus Haessler', version=1.0)

    ENRICHMENT_TYPE: EnrichmentPluginType = EnrichmentPluginType.EXPANSION,
    MISP_ATTRIBUTE: PluginIO = PluginIO(input=['hostname', 'domain'], output=['ip-src', 'ip-dst'])

    def run(self) -> EnrichAttributeResult:
        pass


def register(factory: PluginFactory):
    factory.register(DummyPlugin.PLUGIN_META.NAME, DummyPlugin)
