from __future__ import annotations

import dataclasses
import os
from dataclasses import dataclass
from typing import TypeVar

import numpy as np
import pandas as pd

from meetupmatcher.util.log import logger

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
    availabilities: np.ndarray | None = None,
    rng: np.random.Generator | None = None,
    max_joint_av_boon=5,
    wasted_resource_offset=3,
) -> np.ndarray:
    """Put people in a group of fixed size in a way that helps to maximize the number
    of joint availabilities of each group in the ent.

    Args:
        mask:
        n: Sample/group size
        availabilities:
        rng:
        max_joint_av_boon: This limits the probability boost for joint availabilities.
        wasted_resource_offset: The lower this parameter, the more we punish people with
            many availabilities being assigned to a group where the joint availability
            does not "profit from it"

    Returns:
        Set of indices of people belonging into group
    """
    if n == 0:
        return np.array([], dtype="int")
    if rng is None:
        rng = np.random.RandomState()
    if availabilities is None:
        availabilities = np.full((len(mask), 1), True)
    group = []
    mask = mask.copy()

    def update_availabilities_with_mask(availabilities, mask):
        return availabilities & mask.reshape(-1, 1)

    availabilities = update_availabilities_with_mask(availabilities, mask).copy()
    av_sums: np.ndarray = np.sum(availabilities, axis=1)
    lowest_availability = av_sums[av_sums > 0].min()
    idx_lowest_availabilities = (av_sums == lowest_availability).nonzero()[0]
    idx_first_person = rng.choice(idx_lowest_availabilities)
    assert mask[idx_first_person]
    base_availability = availabilities[idx_first_person]
    group.append(idx_first_person)
    mask[idx_first_person] = False
    availabilities = update_availabilities_with_mask(availabilities, mask)
    n -= 1
    for _ in range(n):
        if mask.sum() == 0:
            raise IncompatibleAvailabilities("Mask is all False.")
        joint_availabilities = availabilities & base_availability
        av_sums = np.sum(availabilities, axis=1)
        joint_av_sums = np.sum(joint_availabilities, axis=1)
        probs = np.min(
            (np.full_like(joint_av_sums, max_joint_av_boon), joint_av_sums), axis=0
        ) / (wasted_resource_offset + av_sums)
        if probs.sum() == 0:
            raise IncompatibleAvailabilities
        probs /= probs.sum()
        idx_next_person = rng.choice(len(mask), p=probs)
        base_availability &= availabilities[idx_next_person]
        mask[idx_next_person] = False
        availabilities = update_availabilities_with_mask(availabilities, mask)
        group.append(idx_next_person)
    return np.array(group)


@dataclass
class PairUpResult:
    #: List of groups given as sets of indices
    segmentation: list[set[int]]
    #: Indices of people that could not be assigned to a group
    removed: set[int]
    #: Join group availabilities as a boolean array of n_people x n_timeslots
    joint_availabilities: np.ndarray = None  # type: ignore

    def __post_init__(self):
        if self.joint_availabilities is None:
            self.joint_availabilities = np.full((len(self.segmentation), 1), 1)
        assert len(self.segmentation) == len(self.joint_availabilities)

    @property
    def av_sums(self) -> np.ndarray:
        return self.joint_availabilities.sum(axis=1)

    @property
    def n_removed(self) -> int:
        return len(self.removed)

    @property
    def min_av_sum(self) -> int:
        return self.av_sums.min()

    # todo: Could do weighting
    @property
    def mean_av_sum(self) -> float:
        return self.av_sums.mean()


def _pair_up(
    sn: SolutionNumbers,
    idx: np.ndarray,
    notwo: np.ndarray,
    availabilities: np.ndarray | None = None,
    *,
    rng: np.random.Generator | None = None,
) -> PairUpResult:
    """ """
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
            new_group_idx = sample(
                this_mask, availabilities=availabilities, n=group_size, rng=rng
            )
            mask[new_group_idx] = False
            segmentation.append(set(idx[new_group_idx]))

    assert mask.sum() == 0
    assert removed | set.union(*segmentation) == set(idx)

    joint_availabilities: None | np.ndarray = None
    if availabilities is not None:
        joint_availabilities = np.array(
            [np.all(availabilities[list(group)], axis=0) for group in segmentation]
        )

    return PairUpResult(
        segmentation, removed, joint_availabilities=joint_availabilities
    )


@dataclasses.dataclass
class PairUpStatistics:
    df: pd.DataFrame
    best: tuple[float, float, float]
    solution_pair_avs: np.ndarray


def pair_up(
    sn: SolutionNumbers,
    idx: np.ndarray,
    notwo: np.ndarray,
    availabilities: np.ndarray | None = None,
    *,
    max_tries=1_000_000,
    abort_after_stable=100,
    rng: np.random.Generator | None = None,
) -> tuple[PairUpResult, PairUpStatistics]:
    if availabilities is None:
        max_tries = 1
    if os.environ.get("MEETUPMATCHER_TESTING"):
        max_tries = 3
    best_solution = None
    n_tries = 0
    n_tries_stable = 0
    best_cost = (-np.inf, -np.inf, -np.inf)
    logger.info("Starting to look for best solution")
    costs = []
    while True:
        n_tries += 1
        try:
            solution = _pair_up(sn, idx, notwo, availabilities, rng=rng)
        except NoSolution:
            continue
        cost = (solution.n_removed, solution.min_av_sum, solution.mean_av_sum)
        if best_solution is None:
            best_solution = solution
        if cost > best_cost:
            best_cost = cost
            best_solution = solution
            n_tries_stable = 0
        else:
            n_tries_stable += 1
        best_cost = max(best_cost, cost)
        costs.append(cost)
        if n_tries >= max_tries:
            logger.info("Reached max tries (%d)", max_tries)
            break
        if n_tries_stable >= abort_after_stable:
            logger.info(
                "Reached stable tries (%d) after %d tries", abort_after_stable, n_tries
            )
            break
    return best_solution, PairUpStatistics(
        pd.DataFrame(costs, columns=["removed", "min_av_sum", "mean_av_sum"]),
        best=best_cost,
        solution_pair_avs=best_solution.joint_availabilities,
    )
