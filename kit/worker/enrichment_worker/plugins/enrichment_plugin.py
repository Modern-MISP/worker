from enum import Enum

from kit.api.worker_router.worker_router import PluginIO
from kit.plugins.plugin import PluginMeta
from kit.worker.enrichment_worker.enrich_attribute_job import EnrichAttributeResult


class EnrichmentPluginType(str, Enum):
    expansion = "expansion"
    hover = "hover"


class EnrichmentPlugin(PluginMeta):
    enrichmentType: EnrichmentPluginType
    mispAttributes: PluginIO

    def process(self) -> EnrichAttributeResult:
        pass
