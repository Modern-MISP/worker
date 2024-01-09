from enum import Enum

from pydantic import Field

from kit.api.job_router.job_router import CorrelateValueResponse
from kit.plugins.plugin import Plugin


class CorrelationPluginType(str, Enum):
    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"


class CorrelationPlugin(Plugin):
    CORRELATION_TYPE: CorrelationPluginType = Field(..., allow_mutation=False)

    def run(self) -> CorrelateValueResponse:
        pass

    def __init__(self, value: str):
        __value: str = value
        pass
