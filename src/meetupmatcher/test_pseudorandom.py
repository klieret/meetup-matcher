from __future__ import annotations

from datetime import datetime

from meetupmatcher.pseudorandom import get_seed_from_option, get_weeks_since_epoch


def test_get_weeks_since_epoch():
    assert (
        get_weeks_since_epoch(
            datetime.timestamp(datetime.strptime("2022-08-08", "%Y-%m-%d"))
        )
        == 2744
    )


def test_get_seed_from_option():
    assert get_seed_from_option("Aug 12 2022") == 2745


def test_get_seed_from_explicit():
    assert get_seed_from_option("2745") == 2745


def test_get_seed_from_nothing():
    assert get_seed_from_option("week") >= 2745
