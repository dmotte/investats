#!/usr/bin/env python3

import pytest

from datetime import date

from investats_gen import Freq


def test_freq():
    assert Freq('weekly') == Freq.WEEKLY

    with pytest.raises(ValueError):
        Freq('foo')

    d = date(2020, 1, 1)

    assert Freq.DAILY.prev(d) == date(2019, 12, 31)
    assert Freq.WEEKLY.prev(d) == date(2019, 12, 25)
    assert Freq.MONTHLY.prev(d) == date(2019, 12, 1)
    assert Freq.YEARLY.prev(d) == date(2019, 1, 1)

    assert Freq.DAILY.next(d) == date(2020, 1, 2)
    assert Freq.WEEKLY.next(d) == date(2020, 1, 8)
    assert Freq.MONTHLY.next(d) == date(2020, 2, 1)
    assert Freq.YEARLY.next(d) == date(2021, 1, 1)

    d = date(2020, 12, 7)

    assert Freq.DAILY.prev(d) == date(2020, 12, 6)
    assert Freq.WEEKLY.prev(d) == date(2020, 11, 30)
    assert Freq.MONTHLY.prev(d) == date(2020, 11, 7)
    assert Freq.YEARLY.prev(d) == date(2019, 12, 7)

    assert Freq.DAILY.next(d) == date(2020, 12, 8)
    assert Freq.WEEKLY.next(d) == date(2020, 12, 14)
    assert Freq.MONTHLY.next(d) == date(2021, 1, 7)
    assert Freq.YEARLY.next(d) == date(2021, 12, 7)
