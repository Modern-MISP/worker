from pydantic import BaseModel


class MispSharingGroupServer(BaseModel):
    """
    Encapsulates a MISP Sharing Group Server.
    """
    all_orgs: bool
    server_id: int
    sharing_group_id: int
    server_id: int | None = None
