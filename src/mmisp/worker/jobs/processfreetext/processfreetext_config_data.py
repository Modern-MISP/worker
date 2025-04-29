from pydantic import Field
from pydantic_settings import BaseSettings

ENV_SECURITY_VENDORS = "PROCESSFREETEXT_SECURITY_VENDORS"

DEFAULT_SECURITY_VENDORS: list[str] = ["virustotal.com", "hybrid-analysis.com"]


class ProcessfreetextConfigData(BaseSettings):
    """
    Encapsulates configuration for the processfreetext worker and its jobs.
    """

    """The security vendors to use for the processfreetext worker."""

    security_vendors: list[str] = Field(DEFAULT_SECURITY_VENDORS, validation_alias=ENV_SECURITY_VENDORS)
