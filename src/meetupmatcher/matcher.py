from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

import numpy as np

T = TypeVar("T")


class NoSolution(Exception):
    pass


class TooFewPeople(NoSolution):
    pass


class IncompatibleAvailabilities(NoSolution):
    pass


@dataclass
class ProblemStatement:
    """All information required to determine the number of groups"""

    #: Total number of people
    n_people: int
    #: The number of people who don't want to be in a group of two
    n_notwo: int

    def __post_init__(self):
        assert self.n_people >= self.n_notwo >= 0


@dataclass
class SolutionNumbers:
    """Number of groups and similar information"""

    #: Number of groups of two, three, four
    partitions: tuple[int, int, int]
    #: Number of people that needed to be removed
    removed: int = 0

    @property
    def n_people(self) -> int:
        """Total number of people"""
        return (
            2 * self.partitions[0]
            + 3 * self.partitions[1]
            + 4 * self.partitions[2]
            + self.removed
        )


def _solve_numeric(ps: ProblemStatement) -> SolutionNumbers:
    if ps.n_people < 2:
        raise TooFewPeople
    elif ps.n_people == 2:
        if ps.n_notwo:
            raise TooFewPeople
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
    mask: np.ndarray,
    n: int,
    rng: np.random.RandomState | None = None,
) -> np.ndarray:
    if rng is None:
        rng = np.random.RandomState()
    return rng.choice(np.arange(len(mask)), size=n, replace=False, p=mask / mask.sum())


# def sample_with_availabilities( source: np.ndarray,
#     n: int,
#     availabilities: np.ndarray | None = None,
#     rng: np.random.Generator | None = None,
#     max_joint_av_boon=5,
#     wasted_resource_offset=3,
# ) -> set[int]:
#     """Put people in a group of fixed size in a way that helps to maximize the number
#     of joint availabilities of each group in the ent.
#
#     Args:
#         source: Sample from here
#         n: Sample/group size
#         availabilities:
#         rng:
#         max_joint_av_boon: This limits the probability boost for joint availabilities.
#         wasted_resource_offset: The lower this parameter, the more we punish people with
#             many availabilities being assigned to a group where the joint availability
#             does not "profit from it"
#
#     Returns:
#         Set of indices of people belonging into group
#     """
#     if rng is None:
#         rng = np.random.RandomState()
#     if availabilities is None:
#         return sample(source=source, n=n, rng=rng)
#     group = []
#     av_sums: np.ndarray = np.sum(availabilities, axis=1)
#     idx_lowest_availabilities = (av_sums == av_sums.min()).nonzero()[0]
#     idx_first_person = rng.choice(idx_lowest_availabilities)
#     base_availability = availabilities[idx_first_person]
#     group.append(source[idx_first_person])
#     source = np.delete(source, idx_first_person)
#     availabilities = np.delete(availabilities, idx_first_person, axis=0)
#     n -= 1
#     print(base_availability.shape)
#     for _ in range(n):
#         joint_availabilities = availabilities & base_availability
#         av_sums = np.sum(availabilities, axis=1)
#         joint_av_sums = np.sum(joint_availabilities, axis=1)
#         probs = np.min((np.ones_like(joint_av_sums), joint_av_sums), axis=0) * (
#             np.min(
#                 (np.full_like(joint_av_sums, max_joint_av_boon), joint_av_sums), axis=0
#             )
#             / (wasted_resource_offset + av_sums)
#         )
#         try:
#             probs /= probs.sum()
#         except ZeroDivisionError:
#             raise IncompatibleAvailabilities
#         idx_next_person = rng.choice(len(source), p=probs)
#         base_availability &= availabilities[idx_next_person]
#         group.append(source[idx_next_person])
#         availabilities = np.delete(availabilities, idx_next_person, axis=0)
#         source = np.delete(source, idx_next_person)
#     return set(group)
#


@dataclass
class PairUpResult:
    #: List of groups given as sets of indices
    segmentation: list[set[int]]
    #: Indices of people that could not be assigned to a group
    removed: set[int]
    #: Join group availabilities as a boolean array of n_people x n_timeslots
    joint_availabilities: np.ndarray | None = None

    def __post_init__(self):
        if self.joint_availabilities is not None:
            assert len(self.segmentation) == len(self.joint_availabilities)


def pair_up(
    sn: SolutionNumbers,
    idx: np.ndarray,
    notwo: np.ndarray,
    rng: np.random.Generator | None = None,
) -> PairUpResult:
    """

    Args:
        sn:
        idx:
        idx_notwo:
        rng:

    Returns:

    """
    assert sn.n_people == len(idx) == len(notwo)
    mask = np.full_like(idx, True)
    segmentation = []
    removed_idxs = sample(mask, n=sn.removed, rng=rng)
    removed = set(idx[removed_idxs])
    mask[removed_idxs] = False
    for i in range(3):
        group_size = i + 2
        n_groups = sn.partitions[i]
        for _ in range(n_groups):
            this_mask = mask.copy()
            if group_size == 2:
                this_mask[notwo] = False
            new_group_idx = sample(this_mask, n=group_size, rng=rng)
            mask[new_group_idx] = False
            segmentation.append(set(idx[new_group_idx]))

    assert mask.sum() == 0
    assert removed | set.union(*segmentation) == set(idx)
    return PairUpResult(segmentation, removed)
