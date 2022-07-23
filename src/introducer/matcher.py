from dataclasses import dataclass

from introducer.data import People


@dataclass
class SolutionCount:
    n_two: int
    n_three: int
    n_move_two_to_three: int
    n_move_three_to_two: int
    n_remove_three_fixed: int
    n_remove_two_fixed: int


def _find_solution(
    n_two: int, n_three: int, n_two_fixed=0, n_three_fixed=0
) -> tuple[int, int]:
    """
    Find a solution to the problem of matching people to groups without removing anyone.

    Args:
        n_two: number of people who prefer groups of two
        n_three: number of people who prefer groups of three
        n_two_fixed: number of people with fixed preference to groups of two
        n_three_fixed: number of people with fixed preference to groups of three

    Returns:
        (number of people in groups of two, number of people in groups of three)
    """
    for move_three_to_two in range(n_three + 1 - n_three_fixed):
        for move_two_to_three in range(n_two + 1 - n_two_fixed):
            real_n_two = n_two - move_two_to_three + move_three_to_two
            real_n_three = n_three + move_two_to_three - move_three_to_two
            assert real_n_two + real_n_three == n_two + n_three
            if real_n_two % 2 == 0 and real_n_three % 3 == 0:
                return real_n_two, real_n_three
    raise ValueError("No solution found")


def _remove_to_pair(n_remove: int) -> tuple[int, int]:
    if n_remove % 2 == 0:
        s = n_remove // 2, n_remove // 2
    else:
        s = n_remove // 2, n_remove // 2 + 1
    assert sum(s) == n_remove
    return s


def find_solution(people: People) -> SolutionCount:
    for n_remove in range(people.n_preference_fixed()):
        remove_three, remove_two = _remove_to_pair(n_remove)
        try:
            n_two, n_three = _find_solution(
                people.n_preference(2) - remove_two,
                people.n_preference(3) - remove_three,
                people.n_preference_fixed(2) - remove_two,
                people.n_preference_fixed(3) - remove_two,
            )
        except ValueError:
            continue
        else:
            return SolutionCount(
                n_two,
                n_three,
                n_move_three_to_two=n_two - people.n_preference(2),
                n_move_two_to_three=n_three - people.n_preference(3),
                n_remove_two_fixed=remove_two,
                n_remove_three_fixed=remove_three,
            )
    raise ValueError("No solution found")


# class Partitioner:
#     def __init__(self):
#         pass
#
#     def partition(self, people: list[Person]) -> list[list[Person]]:
#         pass
