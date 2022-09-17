from __future__ import annotations

import dataclasses
import os
import timeit
from dataclasses import dataclass

import numpy as np
import pandas as pd

from meetupmatcher.util.log import logger


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


def lexicographic_greater(a: np.ndarray, b: np.ndarray) -> bool:
    """Return True if a is lexicographically greater than b"""
    # Numpy 2.0 will likely have a fast "first nonzero" function, see
    # https://github.com/numpy/numpy/issues/2269
    if (a == b).all():
        return False
    idx = np.where(a != b)[0][0]
    return a[idx] > b[idx]


def sample(
    mask: np.ndarray,
    n: int,
    availabilities: np.ndarray | None = None,
    *,
    rng: np.random.Generator | None = None,
    max_joint_av_boon=5,
    wasted_resource_offset=3,
) -> tuple[np.ndarray, int]:
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
        Set of indices of people belonging into group, joint availabilities
    """
    if n == 0:
        return np.array([], dtype="int"), 0
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
    nonzero_av_mask = av_sums > 0
    if not any(nonzero_av_mask):
        raise IncompatibleAvailabilities(
            "Only zero availabilities left, cannot assign people to group"
        )
    lowest_availability = av_sums[nonzero_av_mask].min()
    idx_lowest_availabilities = (av_sums == lowest_availability).nonzero()[0]
    idx_first_person = rng.choice(idx_lowest_availabilities)
    assert mask[idx_first_person]
    base_availability = availabilities[idx_first_person]
    group.append(idx_first_person)
    mask[idx_first_person] = False
    availabilities = update_availabilities_with_mask(availabilities, mask)
    n -= 1
    assert n >= 1
    for _ in range(n):
        if mask.sum() == 0:
            raise IncompatibleAvailabilities("Mask is all False.")
        joint_availabilities = availabilities & base_availability
        av_sums = np.sum(availabilities, axis=1)
        joint_av_sums = np.sum(joint_availabilities, axis=1)
        probs = np.minimum(max_joint_av_boon, joint_av_sums) / (
            wasted_resource_offset + av_sums
        )
        if probs.sum() == 0:
            raise IncompatibleAvailabilities
        probs /= probs.sum()
        idx_next_person = rng.choice(len(mask), p=probs)
        base_availability &= availabilities[idx_next_person]
        mask[idx_next_person] = False
        availabilities = update_availabilities_with_mask(availabilities, mask)
        group.append(idx_next_person)
    return np.array(group), base_availability.sum()


@dataclass
class PairUpResult:
    """Concrete solution that matched people to groups"""

    #: List of groups given as sets of indices
    segmentation: list[set[int]]
    #: Indices of people that could not be assigned to a group
    removed: set[int]
    #: Value of the objective function
    cost: np.ndarray
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

    @property
    def mean_av_sum(self) -> float:
        return self.av_sums.mean()


def _pair_up(
    sn: SolutionNumbers,
    idx: np.ndarray,
    notwo: np.ndarray,
    best_cost: np.ndarray,
    availabilities: np.ndarray | None = None,
    *,
    rng: np.random.Generator | None = None,
) -> PairUpResult | None:
    """Single trial of pairing up people.

    Args:
        sn: SolutionNumbers, specifying the number of groups of each size
        idx:
        notwo: Boolean array: Who vetoes to be in a group of only two-people
        best_cost: Minimal objective function so far
        availabilities: Boolean array of n_people x n_timeslots
        rng: Random number generator

    Returns:
        None if we abort early because the current solution is worse than the best
    """
    assert sn.n_people == len(idx) == len(notwo)
    mask = np.full_like(idx, True)
    segmentation = []
    removed_idxs, _ = sample(mask, n=sn.removed, rng=rng)
    removed = set(idx[removed_idxs])
    mask[removed_idxs] = False
    cost = np.zeros_like(best_cost)
    cost[0] += sn.removed
    for i in range(3):
        group_size = i + 2
        n_groups = sn.partitions[i]

        for _ in range(n_groups):
            this_mask = mask.copy()
            if group_size == 2:
                this_mask[notwo] = False
            new_group_idx, n_joint_availabilities = sample(
                this_mask, availabilities=availabilities, n=group_size, rng=rng
            )
            mask[new_group_idx] = False
            segmentation.append(set(idx[new_group_idx]))
            cost[n_joint_availabilities] += 1
            if lexicographic_greater(cost, best_cost):
                # Abort early
                return None

    assert mask.sum() == 0
    assert removed | set.union(*segmentation) == set(idx)

    joint_availabilities: None | np.ndarray = None
    if availabilities is not None:
        joint_availabilities = np.array(
            [np.all(availabilities[list(group)], axis=0) for group in segmentation]
        )

    return PairUpResult(
        segmentation, removed, joint_availabilities=joint_availabilities, cost=cost
    )


@dataclasses.dataclass
class PairUpStatistics:
    """Statistics about the sampling process that optimizes the objective function"""

    #: DataFrame containing the objective function values for each trial that was
    #: built to the end
    df: pd.DataFrame
    #: Best objective function value
    best: np.ndarray
    #: Availabilities of the best solution
    solution_pair_avs: np.ndarray


def pair_up(
    sn: SolutionNumbers,
    idx: np.ndarray,
    notwo: np.ndarray | None = None,
    availabilities: np.ndarray | None = None,
    *,
    max_tries=1000_000,
    abort_after_stable=100_000,
    rng: np.random.Generator | None = None,
) -> tuple[PairUpResult, PairUpStatistics]:
    """Pair up people by optimizing the objective function over multiple trials.

    Args:
        sn: SolutionNumbers, specifying the number of groups of each size
        idx: Indices of people to be paired up
        notwo: Boolean array: Who vetoes to be in a group of only two-people
        availabilities: Boolean array of n_people x n_timeslots
        max_tries: Maximum number of trials
        abort_after_stable: Abort after this many trials without improvement
        rng: Random number generator

    Returns:
        PairUpResult, PairUpStatistics
    """
    if notwo is None:
        notwo = np.full_like(idx, False)
    if availabilities is None:
        max_tries = 1
        availabilities = np.full((len(idx), 1), 1)
    if os.environ.get("MEETUPMATCHER_TESTING"):
        max_tries = 3
    best_solution = None
    n_tries = 0
    n_tries_stable = 0
    max_availability = np.max(np.sum(availabilities, axis=1))
    best_cost = np.full(max_availability + 1, 0, dtype="int")
    best_cost[0] = sn.n_people
    logger.info("Starting to look for best solution")
    costs = []
    n_full_tries = 0
    t = timeit.default_timer()
    while True:
        if n_tries > max_tries:
            logger.info("Reached max tries (%d)", max_tries)
            break
        if n_tries_stable > abort_after_stable:
            logger.info(
                "Reached stable tries (%d) after %d tries", abort_after_stable, n_tries
            )
            break
        n_tries += 1
        try:
            solution = _pair_up(sn, idx, notwo, best_cost, availabilities, rng=rng)
        except NoSolution:
            continue
        if solution is None:
            # stopped early
            n_tries_stable += 1
            continue
        if best_solution is None:
            best_solution = solution
        if lexicographic_greater(best_cost, solution.cost):
            best_cost = solution.cost
            best_solution = solution
            n_tries_stable = 0
        else:
            n_tries_stable += 1
        n_full_tries += 1
        logger.debug(
            f"tries={n_tries:>10}, full tries={n_full_tries:>3}, best={solution.cost}"
        )
        costs.append(solution.cost)
    elapsed = timeit.default_timer() - t
    logger.info(f"Searched for {elapsed:,} seconds.")
    if best_solution is None:
        raise NoSolution(
            "No solution could be found. You might have to manually remove a "
            "participant"
        )
    return best_solution, PairUpStatistics(
        pd.DataFrame(costs),
        best=best_cost,
        solution_pair_avs=best_solution.joint_availabilities,
    )
