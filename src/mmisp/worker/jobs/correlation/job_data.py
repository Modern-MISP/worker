from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute


class CorrelateValueResponse(BaseModel):
    """
    Response for the correlation of a value.
    """

    success: bool
    found_correlations: bool
    is_excluded_value: bool
    is_over_correlating_value: bool
    plugin_name: Optional[str] = None
    events: Optional[set[UUID]] = None


class TopCorrelationsResponse(BaseModel):
    """
    Response for the top correlations job.
    """

    success: bool
    top_correlations: list[tuple[str, int]]


class DatabaseChangedResponse(BaseModel):
    """
    Response for jobs that only change the database.
    """

    success: bool
    database_changed: bool


class ChangeThresholdResponse(BaseModel):
    """
    Response for the change of the threshold.
    """

    saved: bool
    valid_threshold: bool
    new_threshold: Optional[int] = None


class CorrelationPluginJobData(BaseModel):
    """
    Data for a correlation plugin job.
    """

    value: str
    correlation_plugin_name: str


class CorrelateValueData(BaseModel):
    """
    Data for the correlation of a value.
    """

    value: str


class ChangeThresholdData(BaseModel):
    """
    Data to change the threshold.
    """

    new_threshold: int


class InternPluginResult(BaseModel):
    """
    Result of a plugin to process by the job.
    """

    success: bool
    found_correlations: bool
    is_over_correlating_value: bool
    correlations: list = list[MispFullAttribute]
