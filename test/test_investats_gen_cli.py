#!/usr/bin/env python3

import pytest

from datetime import date

from investats_gen import Freq


def test_freq():
    assert Freq('weekly') == Freq.WEEKLY

    with pytest.raises(ValueError):
        Freq('foo')

    d = date(2020, 1, 1)

    assert Freq.DAILY.next(d) == date(2020, 1, 2)
    assert Freq.WEEKLY.next(d) == date(2020, 1, 8)
    assert Freq.MONTHLY.next(d) == date(2020, 2, 1)
    assert Freq.YEARLY.next(d) == date(2021, 1, 1)
