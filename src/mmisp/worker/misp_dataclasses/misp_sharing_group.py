from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer

from sqlalchemy import Column, Date, DateTime, Index, LargeBinary, String, Table, Text, VARBINARY, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER, LONGTEXT, MEDIUMTEXT, SMALLINT, TEXT, TINYINT, VARCHAR


class MispSharingGroup(BaseModel):
    """
    Encapsulates a MISP Sharing Group.
    """
    id: int
    uuid: UUID
    name: str
    description: str
    releasability: str
    local: bool
    active: bool
    roaming: bool

    created: str | None = None
    modified: str | None = None
    sync_user_id: int | None = None

    organisation: MispOrganisation
    sharing_group_servers: list[MispSharingGroupServer]
    sharing_group_orgs: list[MispSharingGroupOrg]
