import os
from typing import Self

from mmisp.worker.config.config_data import ENV_PREFIX, ConfigData

ENV_SECURITY_VENDORS = f"{ENV_PREFIX}_PROCESSFREETEXT_SECURITY_VENDORS"


class ProcessfreetextConfigData(ConfigData):
    """
    Encapsulates configuration for the processfreetext worker and its jobs.
    """

    security_vendors: list[str] = ["virustotal.com", "hybrid-analysis.com"]
    """The security vendors to use for the processfreetext worker."""

    def __init__(self: Self) -> None:
        super().__init__()
        self.read_from_env()

    def read_from_env(self: Self) -> None:
        """
        Reads the configuration from the environment.
        """

        env_security_vendors: str = os.getenv(ENV_SECURITY_VENDORS, "")
        if env_security_vendors:
            self.security_vendors = env_security_vendors.split(",")
