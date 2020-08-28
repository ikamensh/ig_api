"""
    Limits on available data per resolution:
    Resolution Days
    1 Sec     4
    1 Min     40
    2 Min     40
    3 Min     40
    5 Min     360
    10 Min    360
    15 Min    360
    30 Min    360
    1 Hour    360
    2 Hour    360
    3 Hour    360
    4 Hour    360
    1 Day     15 years

"""
from collections import defaultdict
from datetime import timedelta

from datasets.resolutions import Resolutions as res

default = lambda: timedelta(days=329, hours=23)
limit = defaultdict(default)
limit.update(
    {
        res.SECOND: timedelta(days=3, hours=23),
        res.MINUTE: timedelta(days=39, hours=23),
        res.MINUTE_10: timedelta(days=179, hours=23),
    }
)
