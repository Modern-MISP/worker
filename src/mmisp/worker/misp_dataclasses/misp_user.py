from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator

from mmisp.worker.misp_dataclasses.misp_role import MispRole


class MispUser(BaseModel):
    """
    Encapsulates a MISP User.
    """
    id: int
    password: str
    org_id: int
    email: str
    auto_alert: bool
    invited_by: int
    gpg_key: str | None = None
    certif_public: str | None = None
    nids_sid: int
    terms_accepted: bool
    news_read: int = 0
    role: MispRole
    change_pw: bool
    contact_alert: bool
    disabled: bool
    expiration: datetime | None = None
    current_login: datetime | None = None
    last_login: datetime | None = None
    force_logout: bool
    date_created: datetime | None = None
    date_modified: datetime | None = None
    sub: str | None = None
    external_auth_required: bool = False
    external_auth_key: str | None = None
    last_api_access: datetime | None = None
    notification_daily: bool = False
    notification_weekly: bool = False
    notification_monthly: bool = False
    totp: str | None = None
    hotp_counter: int | None = None
    last_pw_change: datetime = 0
    org_admins: dict[int, str] | None = None

    @field_validator('org_admins', mode='before')
    @classmethod
    def empty_list_to_none(cls, value: Any) -> Any:
        if isinstance(value, list) and len(value) == 0:
            return None
        return value
