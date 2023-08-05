import enum
from typing import Literal, get_args
import typing

class Subjects(enum.Enum):
    UserCreated = 'user:created'

SubjectsValues = Literal['user:created']
assert set(typing.get_args(SubjectsValues)) == {member.value for member in Subjects}