from uuid import UUID

from pydantic import BaseModel


class CorrelateValueResponse(BaseModel):
    success: bool
    foundCorrelations: bool
    isExcludedValue: bool
    isOverCorrelatingValue: bool
    pluginName: str | None
    events: list[UUID] | None


class TopCorrelationsResponse(BaseModel):
    success: bool
    topCorrelations: list[tuple[str, int]]


class DatabaseChangedResponse(BaseModel):
    success: bool
    databaseChanged: bool


class ChangeThresholdResponse(BaseModel):
    saved: bool
    validThreshold: bool
    newThreshold: int | None


class CorrelationPluginJobData(BaseModel):
    value: str
    correlationPluginName: str


class CorrelateValueData(BaseModel):
    value: str


class ChangeThresholdData(BaseModel):
    newThreshold: int
