from mmisp.api_schemas.roles import Role
from mmisp.api_schemas.users import GetUsersUser


class MispUser(GetUsersUser):
    role: Role
