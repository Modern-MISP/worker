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
    gpg_key: str
    certif_public: str
    nids_sid: int
    terms_accepted: bool
    news_read: int
    role: MispRole
    change_pw: bool
    contact_alert: bool
    disabled: bool
    expiration: datetime
    current_login: datetime
    last_login: datetime
    force_logout: bool
    date_created: datetime
    date_modified: datetime
    sub: str
    external_auth_required: bool
    external_auth_key: str
    last_api_access: datetime
    notification_daily: bool
    notification_weekly: bool
    notification_monthly: bool
    totp: str
    hotp_counter: int
    last_pw_change: datetime
    org_admins: dict[int, str]

