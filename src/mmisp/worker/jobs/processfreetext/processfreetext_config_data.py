import os

from mmisp.worker.config_data import ConfigData, ENV_PREFIX
from pydantic import ValidationError

ENV_SECURITY_VENDORS = f"{ENV_PREFIX}_PROCESSFREETEXT_SECURITY_VENDORS"


class ProcessfreetextConfigData(ConfigData):
    """
    Encapsulates configuration for the processfreetext worker and its jobs.
    """
    security_vendors: list[str] = ['virustotal.com', 'hybrid-analysis.com']
    """The security vendors to use for the processfreetext worker."""

    def __init__(self):
        super().__init__()
        self.read_from_env()

    def read_from_env(self):
        """
        Reads the configuration from the environment.
        """

        env_security_vendors: str = os.environ.get(ENV_SECURITY_VENDORS),
        if env_security_vendors is not None:
            self.security_vendors = env_security_vendors.split(',')
