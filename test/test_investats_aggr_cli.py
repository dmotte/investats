#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import datetime as dt
from datetime import timezone as tz

from investats_aggr import pair_items_to_dict, load_data, aggregate_series


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
    data_aaa = [
        {'datetime': dt(2020, 1, 12).astimezone(),
         'diff_days': 0, 'tot_days': 0,
         'diff_src': 500, 'diff_dst': 5, 'latest_rate': 100,
         'tot_src': 500, 'tot_dst': 5, 'avg_rate': 100,
         'tot_dst_as_src': 500,
         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0, 'global_apy': 0,
         'latest_cgt': 0,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0, 'tot_gain_net_src': 0},
        {'datetime': dt(2020, 2, 12).astimezone(),
         'diff_days': 31, 'tot_days': 31,
         'diff_src': 700, 'diff_dst': 10, 'latest_rate': 70,
         'tot_src': 1200, 'tot_dst': 15, 'avg_rate': 80,
         'tot_dst_as_src': 1050,
         'chkpt_yield': -0.30000000000000004, 'chkpt_apy': -0.9849978210304741,
         'global_yield': -0.125, 'global_apy': -0.7924170918049609,
         'latest_cgt': 0.15,
         'chkpt_gain_src': -150, 'chkpt_gain_net_src': -127.5,
         'tot_gain_src': -150, 'tot_gain_net_src': -127.5},
        {'datetime': dt(2020, 3, 12).astimezone(),
         'diff_days': 29, 'tot_days': 60,
         'diff_src': 250, 'diff_dst': 4.25, 'latest_rate': 200,
         'tot_src': 1450, 'tot_dst': 19.25, 'avg_rate': 75.32467532467533,
         'tot_dst_as_src': 3850,
         'chkpt_yield': 1.8571428571428572, 'chkpt_apy': 547587.0028295065,
         'global_yield': 1.6551724137931032, 'global_apy': 379.0996102191754,
         'latest_cgt': 0.15,
         'chkpt_gain_src': 2550, 'chkpt_gain_net_src': 2167.5,
         'tot_gain_src': 2400, 'tot_gain_net_src': 2040},
    ]
    data_bbb = [
        {'datetime': dt(2020, 1, 12).astimezone(),
         'diff_days': 0, 'tot_days': 0,
         'diff_src': 500, 'diff_dst': 10, 'latest_rate': 50,
         'tot_src': 500, 'tot_dst': 10, 'avg_rate': 50,
         'tot_dst_as_src': 500,
         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0, 'global_apy': 0,
         'latest_cgt': 0,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0, 'tot_gain_net_src': 0},
        {'datetime': dt(2020, 2, 12).astimezone(),
         'diff_days': 31, 'tot_days': 31,
         'diff_src': 1400, 'diff_dst': 20, 'latest_rate': 70,
         'tot_src': 1900, 'tot_dst': 30, 'avg_rate': 63.333333333333336,
         'tot_dst_as_src': 2100,
         'chkpt_yield': 0.3999999999999999, 'chkpt_apy': 51.546013724696195,
         'global_yield': 0.10526315789473673, 'global_apy': 2.249177905018738,
         'latest_cgt': 0.20,
         'chkpt_gain_src': 200, 'chkpt_gain_net_src': 160,
         'tot_gain_src': 200, 'tot_gain_net_src': 160},
        {'datetime': dt(2020, 3, 12).astimezone(),
         'diff_days': 29, 'tot_days': 60,
         'diff_src': 250, 'diff_dst': 4.25, 'latest_rate': 200,
         'tot_src': 2150, 'tot_dst': 34.25, 'avg_rate': 62.77372262773723,
         'tot_dst_as_src': 6850,
         'chkpt_yield': 1.8571428571428572, 'chkpt_apy': 547587.0028295065,
         'global_yield': 2.186046511627907, 'global_apy': 1150.9943403101925,
         'latest_cgt': 0.20,
         'chkpt_gain_src': 4500, 'chkpt_gain_net_src': 3600,
         'tot_gain_src': 4700, 'tot_gain_net_src': 3760},
    ]

    named_series = {'AAA': data_aaa, 'BBB': data_bbb}

    # assert list(aggregate_series(named_series)) == [] # TODO

    # TODO check errors with pytest.raises
