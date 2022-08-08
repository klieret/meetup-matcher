from datetime import datetime

from teatimematcher.pseudorandom import get_weeks_since_epoch


def test_get_weeks_since_epoch():
    assert (
        get_weeks_since_epoch(
            datetime.timestamp(datetime.strptime("2022-08-08", "%Y-%m-%d"))
        )
        == 2744
    )
