from __future__ import annotations

import time

import dateutil
import numpy as np

from meetupmatcher.util.log import logger


def get_weeks_since_epoch(timestamp: float = None) -> int:
    """
    Returns the number of weeks since epoch.
    """
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp / (60 * 60 * 24 * 7))


def get_random_seed_from_timestamp(timestamp: float = None) -> int:
    return get_weeks_since_epoch(timestamp)


def get_seed_from_option(option: str) -> int:
    if option == "week":
        return get_random_seed_from_timestamp()
    elif option.isnumeric():
        return int(option)
    else:
        try:
            dt = dateutil.parser.parse(option)
            return get_random_seed_from_timestamp(dt.timestamp())
        except Exception as e:
            raise NotImplementedError(
                f"Unsupported option for the RNG seed: {option}"
            ) from e


def get_rng(timestamp: float = None) -> np.random.Generator:
    seed = get_random_seed_from_timestamp(timestamp=timestamp)
    logger.info(f"Seed set to {seed}")
    return np.random.default_rng(seed)


def get_rng_from_option(option: str) -> np.random.Generator:
    return get_rng(get_seed_from_option(option))
