import time

import numpy as np


def get_weeks_since_epoch(timestamp: float = None) -> int:
    """
    Returns the number of weeks since epoch.
    """
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp / (60 * 60 * 24 * 7))


def get_random_seed(timestamp: float = None) -> int:
    return get_weeks_since_epoch(timestamp)


def get_rng(timestamp: float = None) -> np.random.Generator:
    return np.random.default_rng(get_random_seed(timestamp=timestamp))


def get_rng_from_option(option: str) -> np.random.Generator:
    if option == "week":
        return get_rng()
    elif option.isnumeric():
        return get_rng(int(option))
    else:
        raise NotImplementedError(f"Unknown option for the RNG seed: {option}")
