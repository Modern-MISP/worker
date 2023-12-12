from enum import Enum

from kit.api.worker_router.worker_router import PluginIO
from kit.plugins.plugin import Plugin


class EnrichmentPluginType(str, Enum):
    expansion = "expansion"
    hover = "hover"


class EnrichmentPlugin(Plugin):
    enrichmentType: EnrichmentPluginType
    mispAttributes: PluginIO
