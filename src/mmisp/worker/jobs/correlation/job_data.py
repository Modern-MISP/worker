from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute


class CorrelateValueResponse(BaseModel):
    success: bool
    found_correlations: bool
    is_excluded_value: bool
    is_over_correlating_value: bool
    plugin_name: Optional[str] = None
    events: Optional[set[UUID]] = None


class TopCorrelationsResponse(BaseModel):
    success: bool
    top_correlations: list[tuple[str, int]]


class DatabaseChangedResponse(BaseModel):
    success: bool
    database_changed: bool


class ChangeThresholdResponse(BaseModel):
    saved: bool
    valid_threshold: bool
    new_threshold: Optional[int] = None


class CorrelationPluginJobData(BaseModel):
    value: str
    correlation_plugin_name: str


class CorrelateValueData(BaseModel):
    value: str


class ChangeThresholdData(BaseModel):
    new_threshold: int


class InternPluginResult(BaseModel):
    success: bool
    found_correlations: bool
    is_over_correlating_value: bool
    correlations: list = list[MispEventAttribute]
