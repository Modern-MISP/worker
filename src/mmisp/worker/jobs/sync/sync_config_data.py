import os
from typing import Self

from mmisp.worker.config.config_data import ENV_PREFIX, ConfigData

ENV_ENABLE_EVENT_BLOCKLISTING = f"{ENV_PREFIX}MISP.enableEventBlocklisting"
ENV_ENABLE_ORG_BLOCKLISTING = f"{ENV_PREFIX}MISP.enableOrgBlocklisting"
ENV_HOST_ORG_ID = f"{ENV_PREFIX}MISP.host_org_id"

DEFAULT_ENABLE_EVENT_BLOCKLISTING = False
DEFAULT_ENABLE_ORG_BLOCKLISTING = False
DEFAULT_HOST_ORG_ID = 0


class SyncConfigData(ConfigData):
    """
    Encapsulates the configuration of the sync workers.
    """

    misp_enable_event_blocklisting: bool = DEFAULT_ENABLE_EVENT_BLOCKLISTING
    misp_enable_org_blocklisting: bool = DEFAULT_ENABLE_ORG_BLOCKLISTING
    misp_host_org_id: int = DEFAULT_HOST_ORG_ID

    def read_config_from_env(self: Self) -> None:
        """
        Reads the configuration of the sync workers from environment variables.
        :return: None
        """

        event_blocklist: str = os.environ.get(ENV_ENABLE_EVENT_BLOCKLISTING)
        if event_blocklist:
            self.misp_enable_event_blocklisting = event_blocklist.lower() == "true"

        org_blocklist: str = os.environ.get(ENV_ENABLE_ORG_BLOCKLISTING)
        if org_blocklist:
            self.misp_enable_org_blocklisting = org_blocklist.lower() == "true"

        host_org_id: str = os.environ.get(ENV_HOST_ORG_ID)
        if host_org_id:
            self.misp_host_org_id = int(host_org_id)


sync_config_data: SyncConfigData = SyncConfigData()
sync_config_data.read_config_from_env()
