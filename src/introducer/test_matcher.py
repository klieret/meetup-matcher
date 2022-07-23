from pytest import raises

from introducer.matcher import find_solution


def test_find_solution():
    for n_two in range(10):
        for n_three in range(10):
            if 0 < n_two + n_three < 2:
                with raises(ValueError):
                    find_solution(n_two, n_three)
            else:
                s = find_solution(n_two, n_three)
                assert s[0] + s[1] == n_two + n_three
