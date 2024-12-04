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

    assert list(aggregate_series(named_series)) == [
        {'datetime': dt(2020, 1, 12).astimezone(),
         'diff_days': 0, 'tot_days': 0,

         'diff_src': 1000, 'tot_src': 1000, 'tot_dst_as_src': 1000,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0, 'tot_gain_net_src': 0,

         'AAA:diff_src': 500, 'AAA:diff_dst': 5, 'AAA:latest_rate': 100,
         'AAA:tot_src': 500, 'AAA:tot_dst': 5, 'AAA:avg_rate': 100,
         'AAA:tot_dst_as_src': 500,
         'AAA:chkpt_yield': 0, 'AAA:chkpt_apy': 0,
         'AAA:global_yield': 0, 'AAA:global_apy': 0,
         'AAA:latest_cgt': 0,
         'AAA:chkpt_gain_src': 0, 'AAA:chkpt_gain_net_src': 0,
         'AAA:tot_gain_src': 0, 'AAA:tot_gain_net_src': 0,

         'BBB:diff_src': 500, 'BBB:diff_dst': 10, 'BBB:latest_rate': 50,
         'BBB:tot_src': 500, 'BBB:tot_dst': 10, 'BBB:avg_rate': 50,
         'BBB:tot_dst_as_src': 500,
         'BBB:chkpt_yield': 0, 'BBB:chkpt_apy': 0,
         'BBB:global_yield': 0, 'BBB:global_apy': 0,
         'BBB:latest_cgt': 0,
         'BBB:chkpt_gain_src': 0, 'BBB:chkpt_gain_net_src': 0,
         'BBB:tot_gain_src': 0, 'BBB:tot_gain_net_src': 0,

         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0, 'global_apy': 0},

        {'datetime': dt(2020, 2, 12).astimezone(),
         'diff_days': 31, 'tot_days': 31,

         'diff_src': 2100, 'tot_src': 3100, 'tot_dst_as_src': 3150,
         'chkpt_gain_src': 50, 'chkpt_gain_net_src': 32.5,
         'tot_gain_src': 50, 'tot_gain_net_src': 32.5,

         'AAA:diff_src': 700, 'AAA:diff_dst': 10, 'AAA:latest_rate': 70,
         'AAA:tot_src': 1200, 'AAA:tot_dst': 15, 'AAA:avg_rate': 80,
         'AAA:tot_dst_as_src': 1050,
         'AAA:chkpt_yield': -0.30000000000000004, 'AAA:chkpt_apy': -0.9849978210304741,
         'AAA:global_yield': -0.125, 'AAA:global_apy': -0.7924170918049609,
         'AAA:latest_cgt': 0.15,
         'AAA:chkpt_gain_src': -150, 'AAA:chkpt_gain_net_src': -127.5,
         'AAA:tot_gain_src': -150, 'AAA:tot_gain_net_src': -127.5,

         'BBB:diff_src': 1400, 'BBB:diff_dst': 20, 'BBB:latest_rate': 70,
         'BBB:tot_src': 1900, 'BBB:tot_dst': 30, 'BBB:avg_rate': 63.333333333333336,
         'BBB:tot_dst_as_src': 2100,
         'BBB:chkpt_yield': 0.3999999999999999, 'BBB:chkpt_apy': 51.546013724696195,
         'BBB:global_yield': 0.10526315789473673, 'BBB:global_apy': 2.249177905018738,
         'BBB:latest_cgt': 0.20,
         'BBB:chkpt_gain_src': 200, 'BBB:chkpt_gain_net_src': 160,
         'BBB:tot_gain_src': 200, 'BBB:tot_gain_net_src': 160,

         'chkpt_yield': 0.05, 'chkpt_apy': 0.7761797254076475,
         'global_yield': 0.05, 'global_apy': 0.7761797254076475},

        {'datetime': dt(2020, 3, 12).astimezone(),
         'diff_days': 29, 'tot_days': 60,

         'diff_src': 500, 'tot_src': 3600, 'tot_dst_as_src': 10_700,
         'chkpt_gain_src': 7050, 'chkpt_gain_net_src': 5767.5,
         'tot_gain_src': 7100, 'tot_gain_net_src': 5800,

         'AAA:diff_src': 250, 'AAA:diff_dst': 4.25, 'AAA:latest_rate': 200,
         'AAA:tot_src': 1450, 'AAA:tot_dst': 19.25, 'AAA:avg_rate': 75.32467532467533,
         'AAA:tot_dst_as_src': 3850,
         'AAA:chkpt_yield': 1.8571428571428572, 'AAA:chkpt_apy': 547587.0028295065,
         'AAA:global_yield': 1.6551724137931032, 'AAA:global_apy': 379.0996102191754,
         'AAA:latest_cgt': 0.15,
         'AAA:chkpt_gain_src': 2550, 'AAA:chkpt_gain_net_src': 2167.5,
         'AAA:tot_gain_src': 2400, 'AAA:tot_gain_net_src': 2040,

         'BBB:diff_src': 250, 'BBB:diff_dst': 4.25, 'BBB:latest_rate': 200,
         'BBB:tot_src': 2150, 'BBB:tot_dst': 34.25, 'BBB:avg_rate': 62.77372262773723,
         'BBB:tot_dst_as_src': 6850,
         'BBB:chkpt_yield': 1.8571428571428572, 'BBB:chkpt_apy': 547587.0028295065,
         'BBB:global_yield': 2.186046511627907, 'BBB:global_apy': 1150.9943403101925,
         'BBB:latest_cgt': 0.20,
         'BBB:chkpt_gain_src': 4500, 'BBB:chkpt_gain_net_src': 3600,
         'BBB:tot_gain_src': 4700, 'BBB:tot_gain_net_src': 3760,

         'chkpt_yield': 2.238095238095238, 'chkpt_apy': 2646126.1510352483,
         'global_yield': 7.1, 'global_apy': 336214.0873987736},
    ]

    # TODO check errors with pytest.raises
