from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, TypeVar

import numpy as np

T = TypeVar("T")


class NoSolution(Exception):
    pass


@dataclass
class ProblemStatement:
    n_people: int
    #: The number of people who don't want to be in a group of two
    n_notwo: int

    def __post_init__(self):
        assert self.n_people >= self.n_notwo >= 0


@dataclass
class SolutionNumbers:
    #: Number of groups of two, three, four
    partitions: tuple[int, int, int]
    removed: int = 0

    @property
    def n_people(self) -> int:
        return (
            2 * self.partitions[0]
            + 3 * self.partitions[1]
            + 4 * self.partitions[2]
            + self.removed
        )


def _solve_numeric(ps: ProblemStatement) -> SolutionNumbers:
    if ps.n_people < 2:
        raise NoSolution
    elif ps.n_people == 2:
        if ps.n_notwo:
            raise NoSolution
        else:
            return SolutionNumbers((1, 0, 0))
    elif ps.n_people == 3:
        return SolutionNumbers((0, 1, 0))
    elif ps.n_people == 4:
        return SolutionNumbers((0, 0, 1))
    elif ps.n_people == 5:
        if ps.n_notwo <= 3:
            return SolutionNumbers((1, 1, 0))
        else:
            return SolutionNumbers((0, 0, 1), removed=1)
    elif ps.n_people == 6:
        return SolutionNumbers((0, 2, 0))
    elif ps.n_people == 7:
        return SolutionNumbers((0, 1, 1))
    elif ps.n_people == 8:
        return SolutionNumbers((0, 0, 2))
    else:
        s = _solve_numeric(ProblemStatement(ps.n_people - 3, max(0, ps.n_notwo - 3)))
        assert s.removed == 0
        return SolutionNumbers((s.partitions[0], s.partitions[1] + 1, s.partitions[2]))


def solve_numeric(ps: ProblemStatement) -> SolutionNumbers:
    s = _solve_numeric(ps)
    assert s.n_people == ps.n_people
    return s


def sample(
    source: Iterable[T], n: int, rng: np.random.RandomState | None = None
) -> set[T]:
    if rng is None:
        rng = np.random.RandomState()
    return set(rng.choice(list(source), size=n, replace=False))


@dataclass
class PairUpResult:
    segmentation: list[set[int]]
    removed: set[int]


def pair_up(
    sn: SolutionNumbers,
    idx: set[int],
    idx_notwo: set[int],
    rng: np.random.Generator | None = None,
) -> PairUpResult:
    assert sn.n_people == len(idx) + len(idx_notwo)

    segmentation = []
    removed = sample(idx_notwo, n=sn.removed, rng=rng)
    idx_notwo -= removed
    for i in range(3):
        group_size = i + 2
        n_groups = sn.partitions[i]
        for _ in range(n_groups):
            if group_size > 2:
                pool = idx | idx_notwo
            else:
                pool = idx
            new_group = sample(pool, n=group_size, rng=rng)
            segmentation.append(new_group)
            idx -= new_group
            idx_notwo -= new_group

    assert len(idx) == 0, idx
    assert len(idx_notwo) == 0, idx_notwo
    assert sum(map(len, segmentation))
    return PairUpResult(segmentation, removed)
