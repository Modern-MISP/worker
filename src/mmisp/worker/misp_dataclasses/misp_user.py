from mmisp.api_schemas.roles import Role
from mmisp.api_schemas.users import User


class MispUser(User):
    role = Role
