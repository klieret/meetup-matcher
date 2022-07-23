from dataclasses import dataclass
from enum import Enum, auto


class GroupPreference(Enum):
    two = auto()
    three = auto()
    two_or_three = auto()


@dataclass
class Person:
    name: str
    email: str = ""
    group_preference: GroupPreference = GroupPreference.two_or_three
    n_sessions = 1
