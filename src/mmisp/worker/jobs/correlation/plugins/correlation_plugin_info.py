from enum import Enum

from mmisp.plugins.plugin_info import PluginInfo


class CorrelationPluginType(str, Enum):
    """
    Enum for the type of correlation plugin.
    """

    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"
    OTHER = "other"


class CorrelationPluginInfo(PluginInfo):
    """
    Class to hold information about a correlation plugin.
    """

    CORRELATION_TYPE: CorrelationPluginType
