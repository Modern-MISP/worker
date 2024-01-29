from enum import Enum

from mmisp.worker.plugins.plugin import PluginInfo


class CorrelationPluginType(str, Enum):
    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"


class CorrelationPluginInfo(PluginInfo):
    CORRELATION_TYPE: CorrelationPluginType
