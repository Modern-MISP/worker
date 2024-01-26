from mmisp.worker.misp_dataclasses.misp_object import MispObject


class MispSharingGroupServer(MispObject):
    all_orgs: bool
    server_id: int
    sharing_group_id: int
    server_name: str