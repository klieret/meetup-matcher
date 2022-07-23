from pytest import raises

from introducer.matcher import _find_solution


def test_find_solution():
    for n_two in range(10):
        for n_three in range(10):
            if 0 < n_two + n_three < 2:
                with raises(ValueError):
                    _find_solution(n_two, n_three)
            else:
                s = _find_solution(n_two, n_three)
                assert s[0] + s[1] == n_two + n_three
