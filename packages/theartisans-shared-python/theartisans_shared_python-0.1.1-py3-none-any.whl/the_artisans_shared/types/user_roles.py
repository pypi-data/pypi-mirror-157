import enum
from typing import Literal, get_args

class UserRoles(enum.Enum):
    Normal = 'normal'
    Moderator = 'moderator'
    Developer = 'developer'
    Admin = 'admin'

UserRoleValues = Literal['normal', 'moderator', 'developer', 'admin']
assert set(get_args(UserRoleValues)) == {member.value for member in UserRoles}
