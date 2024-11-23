#!/usr/bin/env python3

from datetime import date

from investats_gen import Freq


def test_freq():
    d = date(2020, 1, 1)

    assert Freq.DAILY.next(d) == date(2020, 1, 2)
