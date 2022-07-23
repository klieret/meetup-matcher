from matcher import find_solution


def test_find_solution():
    for n_two in range(10):
        for n_three in range(10):
            if n_two == 0 and n_three == 0:
                continue
            find_solution(n_two, n_three)
