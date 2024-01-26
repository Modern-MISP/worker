from datetime import datetime

from pydantic import BaseModel


class MispRole(BaseModel):
    id: int
    name: str
    created: datetime
    modified: datetime
    perm_add: bool
    perm_modify: bool
    perm_modify_org: bool
    perm_publish: bool
    perm_delegate: bool
    perm_sync: bool
    perm_admin: bool
    perm_audit: bool
    perm_auth: bool
    perm_site_admin: bool
    perm_regexp_access: bool
    perm_tagger: bool
    perm_template: bool
    perm_sharing_group: bool
    perm_tag_editor: bool
    perm_sighting: bool
    perm_object_template: bool
    default_role: bool
    memory_limit: str
    max_execution_time: str
    restricted_to_site_admin: bool
    perm_publish_zmq: bool
    perm_publish_kafka: bool
    perm_decaying: bool
    enforce_rate_limit: bool
    rate_limit_count: int
    perm_galaxy_editor: bool
    perm_warninglist: bool
    perm_view_feed_correlations: bool
    permission: str
    permission_description: str
