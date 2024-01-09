from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    password: str
    org_id: int
    email: str
    autoalert: bool
    invited_by: int
    gpgkey: str
    certif_public: str
    nids_sid: int
    termsaccepted: bool
    newsread: int
    role_id: int
    change_pw: bool
    contactalert: bool
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
    orgAdmins: dict[int, str]

