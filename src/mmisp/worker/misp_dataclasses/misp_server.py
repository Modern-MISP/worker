from typing import Any

from pydantic import BaseModel, field_validator

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation


class Server(BaseModel):
    """
    Encapsulates a MISP Server.
    """
    id: int
    name: str | None = None
    url: str
    push: bool
    pull: bool
    push_sightings: bool
    push_galaxy_clusters: bool
    pull_galaxy_clusters: bool
    last_pulled_id: int | None = None
    last_pushed_id: int | None = None
    organization: MispOrganisation | None = None
    remote_organization: MispOrganisation | None = None
    publish_without_email: bool
    unpublish_event: bool
    self_signed: bool
    pull_rules: str | None = None
    push_rules: str | None = None
    cert_file: str | None = None
    client_cert_file: str | None = None
    internal: bool
    skip_proxy: bool
    remove_missing_tags: bool
    caching_enabled: bool
    priority: int
    cache_timestamp: bool

    @field_validator('cache_timestamp', mode='before')
    @classmethod
    def cache_timestamp_to_val(cls, value: Any) -> Any:
        """
        Method to convert the cache_timestamp value to a boolean.
        :param value: The value to convert.
        :type value: Any
        :return: The converted value.
        """
        if value is None:
            return False
        return True
