from typing import Dict

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation


class MispServer(BaseModel):
    id: int
    name: str
    url: str
    push: bool
    pull: bool
    push_sightings: bool
    push_galaxy_clusters: bool
    pull_galaxy_clusters: bool
    lastpulledid: int
    lastpushedid: int
    organization: MispOrganisation
    remote_organization: MispOrganisation
    publish_without_email: bool
    unpublish_event: bool
    self_signed: bool
    pull_rules: Dict[str, Dict[str, set[str]]]
    push_rules: Dict[str, Dict[str, set[str]]]
    cert_file: str
    client_cert_file: str
    internal: bool
    skip_proxy: bool
    remove_missing_tags: bool
    caching_enabled: bool
    priority: int
    cache_timestamp: bool