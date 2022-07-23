from dataclasses import dataclass
from enum import Enum, auto


class GroupPreference(Enum):
    two = auto()
    three = auto()


@dataclass
class Person:
    name: str
    email: str = ""
    group_preference: GroupPreference = GroupPreference.three
    group_preference_binding = False
    n_sessions = 1
