from typing import Optional

from mmisp.worker.config_data import ConfigData


class CorrelationConfigData(ConfigData):

    threshold: Optional[int] = 20
    path_to_correlation_plugins: Optional[str] = None
