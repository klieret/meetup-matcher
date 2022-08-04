from dataclasses import dataclass

from introducer.data import People
from introducer.util.log import get_logger


def _find_solution_count(
    n_two: int, n_three: int, n_two_fixed=0, n_three_fixed=0
) -> tuple[int, int, int, int]:
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
                return real_n_two, real_n_three, move_three_to_two, move_two_to_three
    raise ValueError("No solution found")


def _remove_to_pair(n_remove: int) -> tuple[int, int]:
    if n_remove % 2 == 0:
        s = n_remove // 2, n_remove // 2
    else:
        s = n_remove // 2, n_remove // 2 + 1
    assert sum(s) == n_remove
    return s


@dataclass
class SolutionCount:
    n_two: int
    n_three: int
    n_move_two_to_three: int
    n_move_three_to_two: int
    n_remove_three_fixed: int
    n_remove_two_fixed: int

    def __post_init__(self):
        for v in self.__dataclass_fields__:
            assert getattr(self, v) >= 0, v


def find_solution_count(people: People) -> SolutionCount:
    for n_remove in range(people.n_preference_fixed()):
        remove_three, remove_two = _remove_to_pair(n_remove)
        try:
            n_two, n_three, move_three_to_two, move_two_to_three = _find_solution_count(
                people.n_preference(2) - remove_two,
                people.n_preference(3) - remove_three,
                people.n_preference_fixed(2) - remove_two,
                people.n_preference_fixed(3) - remove_three,
            )
        except ValueError:
            continue
        else:
            if n_remove:
                get_logger().warning(f"Had to remove {n_remove} people")
            return SolutionCount(
                n_two,
                n_three,
                n_move_three_to_two=move_three_to_two,
                n_move_two_to_three=move_two_to_three,
                n_remove_two_fixed=remove_two,
                n_remove_three_fixed=remove_three,
            )
    raise ValueError("No solution found")


@dataclass
class Solution:
    two: list[int]
    three: list[int]
    removed: list[int]

    def __post_init__(self):
        assert len(self.two) % 2 == 0
        assert len(self.three) % 3 == 0


def _find_solution(people: People, sc: SolutionCount) -> Solution:
    index = people.df.index
    assert len(set(index)) == len(index)
    to_be_removed = (
        people.df.query("(preference == 2) & (fixed == True)")
        .sample(n=sc.n_remove_two_fixed)
        .index.to_list()
    )
    to_be_removed += (
        people.df.query("(preference == 3) & (fixed == True)")
        .sample(n=sc.n_remove_three_fixed)
        .index.to_list()
    )
    remaining = set(index) - set(to_be_removed)
    pool_for_two = (
        people.df.loc[remaining]
        .query("(preference == 3) & (fixed == False)")
        .sample(n=sc.n_move_three_to_two)
        .index.to_list()
    )
    pool_for_two += (
        people.df.loc[remaining]
        .query("preference == 2")
        .sample(n=sc.n_two - sc.n_move_three_to_two)
        .index.to_list()
    )
    remaining = set(remaining) - set(pool_for_two)
    pool_for_three = (
        people.df.loc[remaining]
        .query("(preference == 2) & (fixed == False)")
        .sample(n=sc.n_move_two_to_three)
        .index.to_list()
    )
    pool_for_three += (
        people.df.loc[remaining]
        .query("preference == 3")
        .sample(n=sc.n_three - sc.n_move_two_to_three)
        .index.to_list()
    )
    remaining = set(remaining) - set(pool_for_three)
    assert not remaining
    return Solution(
        two=pool_for_two,
        three=pool_for_three,
        removed=to_be_removed,
    )


def find_solution(people: People) -> Solution:
    return _find_solution(people, find_solution_count(people))


# class Partitioner:
#     def __init__(self):
#         pass
#
#     def partition(self, people: list[Person]) -> list[list[Person]]:
#         pass
