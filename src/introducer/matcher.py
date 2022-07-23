from util import ProgrammingError


def find_solution(n_two: int, n_three: int) -> tuple[int, int]:
    if 0 < n_two + n_three < 2:
        raise ValueError("Impossible to find solution")
    for move_three_to_two in range(n_three + 1):
        for move_two_to_three in range(n_two + 1):
            real_n_two = n_two - move_two_to_three + move_three_to_two
            real_n_three = n_three + move_two_to_three - move_three_to_two
            assert real_n_two + real_n_three == n_two + n_three
            if real_n_two % 2 == 0 and real_n_three % 3 == 0:
                return real_n_two, real_n_three
    raise ProgrammingError("This should be guaranteed to return a solution")
