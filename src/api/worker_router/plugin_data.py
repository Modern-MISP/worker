from typing import List

from pydantic import BaseModel

from src.plugins.plugin import PluginMeta
from src.job.correlation_job.plugins.correlation_plugin import CorrelationPluginType
from src.job.enrichment_job.plugins.enrichment_plugin import EnrichmentPluginType, PluginIO


class EnrichmentPlugin(BaseModel):
    plugin: PluginMeta
    enrichment: dict = {
        "type": EnrichmentPluginType,
        "mispAttributes": PluginIO
    }


class CorrelationPlugin(BaseModel):
    plugin: PluginMeta
    correlationType: CorrelationPluginType


