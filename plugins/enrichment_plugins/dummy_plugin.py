from kit.plugins.factory import PluginFactory
from kit.plugins.plugin import PluginIO, PluginType
from kit.worker.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginType


class DummyPlugin:
    name: str = "dummy-plugin"
    pluginType: PluginType = PluginType.enrichment
    description: str = "Dummy Plugin is a useless plugin."
    author: str = "Amadeus Haessler"
    version: float = 1.0
    enrichmentType: EnrichmentPluginType = EnrichmentPluginType.expansion
    mispAttributes: PluginIO = PluginIO(input=["hostname", "domain"], output=["ip-src", "ip-dst"])

    def process(self) -> object:
        pass


def register(factory: PluginFactory):
    factory.register(DummyPlugin.name, DummyPlugin)
