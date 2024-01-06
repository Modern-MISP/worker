from enum import Enum

from kit.api.worker_router.worker_router import PluginIO
from kit.plugins.plugin import PluginMeta


class CorrelationPluginType(str, Enum):
    default = "oneValue"


class CorrelationPlugin(PluginMeta):
    correlationType: CorrelationPluginType
    mispAttributes: PluginIO
