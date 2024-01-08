from kit.plugins.factory import PluginFactory
from kit.plugins.plugin import PluginType, PluginMeta
from kit.worker.enrichment_job.enrich_attribute_job import EnrichAttributeResult
from kit.worker.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO


class DummyPlugin:
    PLUGIN_META: PluginMeta = PluginMeta(name='dk', pluginType=PluginType.ENRICHMENT,
                                         description='Descriptionjdafja', author='Amadeus Haessler', version=1.0)

    __ENRICHMENT_TYPE: EnrichmentPluginType = EnrichmentPluginType.EXPANSION,
    __MISP_ATTRIBUTE: PluginIO = PluginIO(input=['hostname', 'domain'], output=['ip-src', 'ip-dst'])

    def run(self) -> EnrichAttributeResult:
        pass


def register(factory: PluginFactory):
    factory.register(DummyPlugin.PLUGIN_META.NAME, DummyPlugin)
