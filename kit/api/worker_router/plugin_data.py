from typing import List

from pydantic import BaseModel

from kit.plugins.plugin import PluginMeta
from kit.worker.correlation_job.plugins.correlation_plugin import CorrelationPluginType
from kit.worker.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO


class EnrichmentPlugin(BaseModel):
    plugin: PluginMeta
    enrichment: dict = {
        "type": EnrichmentPluginType,
        "mispAttributes": PluginIO
    }


class CorrelationPlugin(BaseModel):
    plugin: PluginMeta
    correlationType: CorrelationPluginType


class GetEnrichmentPluginsResponse(BaseModel):
    plugins: List[EnrichmentPlugin]


class GetCorrelationPluginsResponse(BaseModel):
    plugins: List[CorrelationPlugin]
