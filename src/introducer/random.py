import time

import numpy as np


def get_weeks_since_epoch(timestamp: float = None):
    """
    Returns the number of weeks since epoch.
    """
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp / (60 * 60 * 24 * 7))


def get_random_seed(timestamp: float = None) -> int:
    return get_weeks_since_epoch(timestamp)


def get_rng(timestamp: float = None):
    return np.random.default_rng(get_random_seed(timestamp=timestamp))