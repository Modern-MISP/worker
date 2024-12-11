import logging
from typing import Self

from mmisp.worker.config import ENV_PREFIX, ConfigData

ENV_FEED_REPO = f"{ENV_PREFIX}_FEED_REPO"

_log = logging.getLogger(__name__)


class ImportfeedConfigData(ConfigData):
    """Encapsulates configuration for the importFeed worker and its jobs.

    This class is responsible for managing and loading configuration data required
    for the importFeed worker. It reads configuration settings, such as security vendors,
    from the environment and makes them available as attributes. It also supports reading
    configuration values specific to the importFeed worker's behavior.
    """

    def __init__(self: Self) -> None:
        """Initializes the ImportfeedConfigData instance."""
        super().__init__()
