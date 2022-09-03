from __future__ import annotations

import numpy as np
from pytest import raises

from meetupmatcher.matcher import (
    NoSolution,
    PairUpResult,
    ProblemStatement,
    SolutionNumbers,
    pair_up,
    solve_numeric,
)

test_cases = {
    (4, 0): (0, 0, 1, 0),
    (11, 0): (0, 1, 2, 0),
    (12, 0): (0, 4, 0, 0),
}


def test_solve_numeric():
    for ps, expected in test_cases.items():
        assert solve_numeric(ProblemStatement(*ps)) == SolutionNumbers(
            expected[:3], removed=expected[3]
        )


def test_solvable():
    for i in range(3, 20):
        for fixed in [0, i]:
            solve_numeric(ProblemStatement(i, fixed))
    solve_numeric(ProblemStatement(2, 0))


def test_not_solvable():
    cases = [
        (0, 0),
        (1, 0),
        (1, 1),
        (2, 1),
        (2, 2),
    ]
    for case in cases:
        with raises(NoSolution):
            solve_numeric(ProblemStatement(*case))


def test_pair_up():
    assert pair_up(
        SolutionNumbers(partitions=(1, 1, 0), removed=0),
        np.arange(5),
        np.array([False, False, True, True, True]),
        rng=np.random.RandomState(0),
    ) == PairUpResult([{0, 1}, {2, 3, 4}], set())
