from pydantic import Field
from pydantic_settings import BaseSettings

ENV_ENABLE_EVENT_BLOCKLISTING = "MISP.enableEventBlocklisting"
ENV_ENABLE_ORG_BLOCKLISTING = "MISP.enableOrgBlocklisting"
ENV_HOST_ORG_ID = "MISP.host_org_id"


class SyncConfigData(BaseSettings):
    """
    Encapsulates the configuration of the sync workers.
    """

    misp_enable_event_blocklisting: bool = Field(False, validation_alias=ENV_ENABLE_EVENT_BLOCKLISTING)
    misp_enable_org_blocklisting: bool = Field(False, validation_alias=ENV_ENABLE_ORG_BLOCKLISTING)
    misp_host_org_id: int = Field(0, validation_alias=ENV_HOST_ORG_ID)


sync_config_data: SyncConfigData = SyncConfigData()
