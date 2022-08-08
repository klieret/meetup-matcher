import numpy as np
from pytest import raises

from teatimematcher.matcher import (
    NoSolution,
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
        {0, 1, 2, 3},
        {
            4,
        },
        rng=np.random.RandomState(0),
    ) == ([{2, 3}, {0, 1, 4}], set())
