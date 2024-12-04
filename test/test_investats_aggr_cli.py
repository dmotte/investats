#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import datetime as dt
from datetime import timezone as tz

from investats_aggr import pair_items_to_dict, load_data


def test_pair_items_to_dict():
    assert pair_items_to_dict(['A', 'aaa', 'B', 'bbb']) == \
        {'A': 'aaa', 'B': 'bbb'}
    assert pair_items_to_dict(['A', 'aaa', 'B', 'bbb', 'C', 'ccc']) == \
        {'A': 'aaa', 'B': 'bbb', 'C': 'ccc'}

    # The length of pair items must be an even number
    with pytest.raises(ValueError):
        pair_items_to_dict(['A', 'aaa', 'B'])

    with pytest.raises(ValueError):  # The number of pairs must be >= 2
        pair_items_to_dict(['A', 'aaa'])


def test_load_data():
    csv = textwrap.dedent('''\
        datetime,field01,field02,field03
        2020-01-01 00:00:00+00:00,0,0,0
        2020-01-12 00:00:00+00:00,11,11,500
        2020-02-12 00:00:00+00:00,31,42,700.123
        2020-03-12 00:00:00+00:00,29,71,250.001
    ''')

    data = list(load_data(io.StringIO(csv)))

    assert data == [
        {'datetime': dt(2020, 1, 1, tzinfo=tz.utc),
         'field01': 0, 'field02': 0, 'field03': 0},
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc),
         'field01': 11, 'field02': 11, 'field03': 500},
        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc),
         'field01': 31, 'field02': 42, 'field03': 700.123},
        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc),
         'field01': 29, 'field02': 71, 'field03': 250.001},
    ]


def test_save_data():
    pass  # TODO


def test_aggregate_series():
    pass  # TODO
