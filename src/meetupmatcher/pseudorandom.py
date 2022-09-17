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
        logger.debug("Using current time for seed")
        timestamp = time.time()
    logger.debug("Timestamp is %s", timestamp)
    n_weeks = int(timestamp / (60 * 60 * 24 * 7))
    if n_weeks == 0:
        raise ValueError("Implausible timestamp")
    return n_weeks


def get_random_seed_from_timestamp(timestamp: float = None) -> int:
    return get_weeks_since_epoch(timestamp)


def get_seed_from_option(option: str) -> int:
    if option == "week":
        logger.debug("Getting seed from week number")
        return get_random_seed_from_timestamp()
    elif option.isnumeric():
        logger.debug("Explicitly setting seed to number")
        return int(option)
    else:
        try:
            dt = dateutil.parser.parse(option)
            return get_random_seed_from_timestamp(dt.timestamp())
        except Exception as e:
            raise NotImplementedError(
                f"Unsupported option for the RNG seed: {option}"
            ) from e


def get_rng_from_seed(seed: float) -> np.random.Generator:
    return np.random.default_rng(seed)


def get_rng_from_option(option: str) -> np.random.Generator:
    logger.debug("Seed option is %s", option)
    seed = get_seed_from_option(option)
    logger.info("Seed is %s", seed)
    return get_rng_from_seed(seed)
