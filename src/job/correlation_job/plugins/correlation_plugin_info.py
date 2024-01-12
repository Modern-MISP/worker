from enum import Enum

from src.plugins.plugin import PluginInfo


class CorrelationPluginType(str, Enum):
    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"


class CorrelationPluginInfo(PluginInfo):
    correlationType: CorrelationPluginType
