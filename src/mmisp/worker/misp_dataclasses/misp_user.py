from datetime import datetime

from pydantic import BaseModel

from mmisp.worker.misp_dataclasses.misp_role import MispRole


class MispUser(BaseModel):
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
    current_login: datetime = 0
    last_login: datetime = 0
    force_logout: bool
    date_created: datetime = 0
    date_modified: datetime = 0
    sub: str | None = None
    external_auth_required: bool
    external_auth_key: str | None = None
    last_api_access: datetime = 0
    notification_daily: bool
    notification_weekly: bool
    notification_monthly: bool
    totp: str | None = None
    hotp_counter: int | None = None
    last_pw_change: datetime = 0
    org_admins: dict[int, str]

