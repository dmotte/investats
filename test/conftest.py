#!/usr/bin/env python3

import pytest

from copy import deepcopy
from datetime import datetime as dt
from datetime import timezone as tz


_data_invstts = [
    {'in': [
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 500, 'rate': 100},
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc), 'type': 'chkpt',
         'notes': 'First checkpoint'},

        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 700, 'rate': 70},
        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc), 'type': 'chkpt',
         'cgt': 0.15},

        {'datetime': dt(2020, 3, 10, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 200, 'rate': 50, 'notes': 'Some notes here'},
        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 50, 'rate': 200},
        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc), 'type': 'chkpt'},
    ], 'out': [
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc),
         'diff_days': 0, 'tot_days': 0,
         'diff_src': 500, 'diff_dst': 5.0, 'latest_rate': 100,
         'tot_src': 500, 'tot_dst': 5.0, 'avg_rate': 100.0,
         'tot_dst_as_src': 500.0,
         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0.0, 'global_apy': 0,
         'latest_cgt': 0,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0.0, 'tot_gain_net_src': 0.0},
        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc),
         'diff_days': 31.0, 'tot_days': 31.0,
         'diff_src': 700, 'diff_dst': 10.0, 'latest_rate': 70,
         'tot_src': 1200, 'tot_dst': 15.0, 'avg_rate': 80.0,
         'tot_dst_as_src': 1050.0,
         'chkpt_yield': -0.30000000000000004, 'chkpt_apy': -0.9849978210304741,
         'global_yield': -0.125, 'global_apy': -0.7924170918049609,
         'latest_cgt': 0.15,
         'chkpt_gain_src': -150.0, 'chkpt_gain_net_src': -127.5,
         'tot_gain_src': -150.0, 'tot_gain_net_src': -127.5},
        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc),
         'diff_days': 29.0, 'tot_days': 60.0,
         'diff_src': 250, 'diff_dst': 4.25, 'latest_rate': 200,
         'tot_src': 1450, 'tot_dst': 19.25, 'avg_rate': 75.32467532467533,
         'tot_dst_as_src': 3850.0,
         'chkpt_yield': 1.8571428571428572, 'chkpt_apy': 547587.0028295065,
         'global_yield': 1.6551724137931032, 'global_apy': 379.0996102191754,
         'latest_cgt': 0.15,
         'chkpt_gain_src': 2550.0, 'chkpt_gain_net_src': 2167.5,
         'tot_gain_src': 2400.0, 'tot_gain_net_src': 2040.0},
    ]},
    {'in': [
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 500, 'rate': 50},
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc), 'type': 'chkpt'},

        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 1400, 'rate': 70},
        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc), 'type': 'chkpt',
         'cgt': 0.20},

        {'datetime': dt(2020, 3, 10, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 200, 'rate': 50},
        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc), 'type': 'invest',
         'inv_src': 50, 'rate': 200},
        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc), 'type': 'chkpt'},
    ], 'out': [
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc),
         'diff_days': 0, 'tot_days': 0,
         'diff_src': 500, 'diff_dst': 10.0, 'latest_rate': 50,
         'tot_src': 500, 'tot_dst': 10.0, 'avg_rate': 50.0,
         'tot_dst_as_src': 500.0,
         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0.0, 'global_apy': 0,
         'latest_cgt': 0,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0.0, 'tot_gain_net_src': 0.0},
        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc),
         'diff_days': 31.0, 'tot_days': 31.0,
         'diff_src': 1400, 'diff_dst': 20.0, 'latest_rate': 70,
         'tot_src': 1900, 'tot_dst': 30.0, 'avg_rate': 63.333333333333336,
         'tot_dst_as_src': 2100.0,
         'chkpt_yield': 0.3999999999999999, 'chkpt_apy': 51.546013724696195,
         'global_yield': 0.10526315789473673, 'global_apy': 2.249177905018738,
         'latest_cgt': 0.20,
         'chkpt_gain_src': 200.0, 'chkpt_gain_net_src': 160.0,
         'tot_gain_src': 200.0, 'tot_gain_net_src': 160.0},
        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc),
         'diff_days': 29.0, 'tot_days': 60.0,
         'diff_src': 250, 'diff_dst': 4.25, 'latest_rate': 200,
         'tot_src': 2150, 'tot_dst': 34.25, 'avg_rate': 62.77372262773723,
         'tot_dst_as_src': 6850.0,
         'chkpt_yield': 1.8571428571428572, 'chkpt_apy': 547587.0028295065,
         'global_yield': 2.186046511627907, 'global_apy': 1150.9943403101925,
         'latest_cgt': 0.20,
         'chkpt_gain_src': 4500.0, 'chkpt_gain_net_src': 3600.0,
         'tot_gain_src': 4700.0, 'tot_gain_net_src': 3760.0},
    ]},
]


@pytest.fixture
def get_data_invstts():
    def factory(id: int = -1, side: str = ''):
        if id < 0:
            return deepcopy(_data_invstts)
        if side == '':
            return deepcopy(_data_invstts[id])
        return deepcopy(_data_invstts[id][side])

    return factory


_data_invsttsaggr = [
    {'in': {
        'AAA': _data_invstts[0]['out'],
        'BBB': _data_invstts[1]['out'],
    }, 'out': [
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc),
         'diff_days': 0, 'tot_days': 0,

         'diff_src': 1000, 'tot_src': 1000, 'tot_dst_as_src': 1000.0,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0.0, 'tot_gain_net_src': 0.0,

         'AAA:diff_days': 0, 'AAA:tot_days': 0,
         'AAA:diff_src': 500, 'AAA:diff_dst': 5.0, 'AAA:latest_rate': 100,
         'AAA:tot_src': 500, 'AAA:tot_dst': 5.0, 'AAA:avg_rate': 100.0,
         'AAA:tot_dst_as_src': 500.0,
         'AAA:chkpt_yield': 0, 'AAA:chkpt_apy': 0,
         'AAA:global_yield': 0.0, 'AAA:global_apy': 0,
         'AAA:latest_cgt': 0,
         'AAA:chkpt_gain_src': 0, 'AAA:chkpt_gain_net_src': 0,
         'AAA:tot_gain_src': 0.0, 'AAA:tot_gain_net_src': 0.0,

         'BBB:diff_days': 0, 'BBB:tot_days': 0,
         'BBB:diff_src': 500, 'BBB:diff_dst': 10.0, 'BBB:latest_rate': 50,
         'BBB:tot_src': 500, 'BBB:tot_dst': 10.0, 'BBB:avg_rate': 50.0,
         'BBB:tot_dst_as_src': 500.0,
         'BBB:chkpt_yield': 0, 'BBB:chkpt_apy': 0,
         'BBB:global_yield': 0.0, 'BBB:global_apy': 0,
         'BBB:latest_cgt': 0,
         'BBB:chkpt_gain_src': 0, 'BBB:chkpt_gain_net_src': 0,
         'BBB:tot_gain_src': 0.0, 'BBB:tot_gain_net_src': 0.0,

         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0.0, 'global_apy': 0},

        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc),
         'diff_days': 31.0, 'tot_days': 31.0,

         'diff_src': 2100, 'tot_src': 3100, 'tot_dst_as_src': 3150.0,
         'chkpt_gain_src': 50.0, 'chkpt_gain_net_src': 32.5,
         'tot_gain_src': 50.0, 'tot_gain_net_src': 32.5,

         'AAA:diff_days': 31.0, 'AAA:tot_days': 31.0,
         'AAA:diff_src': 700, 'AAA:diff_dst': 10.0, 'AAA:latest_rate': 70,
         'AAA:tot_src': 1200, 'AAA:tot_dst': 15.0, 'AAA:avg_rate': 80.0,
         'AAA:tot_dst_as_src': 1050.0,
         'AAA:chkpt_yield': -0.30000000000000004, 'AAA:chkpt_apy': -0.9849978210304741,
         'AAA:global_yield': -0.125, 'AAA:global_apy': -0.7924170918049609,
         'AAA:latest_cgt': 0.15,
         'AAA:chkpt_gain_src': -150.0, 'AAA:chkpt_gain_net_src': -127.5,
         'AAA:tot_gain_src': -150.0, 'AAA:tot_gain_net_src': -127.5,

         'BBB:diff_days': 31.0, 'BBB:tot_days': 31.0,
         'BBB:diff_src': 1400, 'BBB:diff_dst': 20.0, 'BBB:latest_rate': 70,
         'BBB:tot_src': 1900, 'BBB:tot_dst': 30.0, 'BBB:avg_rate': 63.333333333333336,
         'BBB:tot_dst_as_src': 2100.0,
         'BBB:chkpt_yield': 0.3999999999999999, 'BBB:chkpt_apy': 51.546013724696195,
         'BBB:global_yield': 0.10526315789473673, 'BBB:global_apy': 2.249177905018738,
         'BBB:latest_cgt': 0.20,
         'BBB:chkpt_gain_src': 200.0, 'BBB:chkpt_gain_net_src': 160.0,
         'BBB:tot_gain_src': 200.0, 'BBB:tot_gain_net_src': 160.0,

         'chkpt_yield': 0.05, 'chkpt_apy': 0.7761797254076475,
         'global_yield': 0.016129032258064516, 'global_apy': 0.20730561938737058},

        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc),
         'diff_days': 29.0, 'tot_days': 60.0,

         'diff_src': 500, 'tot_src': 3600, 'tot_dst_as_src': 10_700.0,
         'chkpt_gain_src': 7050.0, 'chkpt_gain_net_src': 5767.5,
         'tot_gain_src': 7100.0, 'tot_gain_net_src': 5800.0,

         'AAA:diff_days': 29.0, 'AAA:tot_days': 60.0,
         'AAA:diff_src': 250, 'AAA:diff_dst': 4.25, 'AAA:latest_rate': 200,
         'AAA:tot_src': 1450, 'AAA:tot_dst': 19.25, 'AAA:avg_rate': 75.32467532467533,
         'AAA:tot_dst_as_src': 3850.0,
         'AAA:chkpt_yield': 1.8571428571428572, 'AAA:chkpt_apy': 547587.0028295065,
         'AAA:global_yield': 1.6551724137931032, 'AAA:global_apy': 379.0996102191754,
         'AAA:latest_cgt': 0.15,
         'AAA:chkpt_gain_src': 2550.0, 'AAA:chkpt_gain_net_src': 2167.5,
         'AAA:tot_gain_src': 2400.0, 'AAA:tot_gain_net_src': 2040.0,

         'BBB:diff_days': 29.0, 'BBB:tot_days': 60.0,
         'BBB:diff_src': 250, 'BBB:diff_dst': 4.25, 'BBB:latest_rate': 200,
         'BBB:tot_src': 2150, 'BBB:tot_dst': 34.25, 'BBB:avg_rate': 62.77372262773723,
         'BBB:tot_dst_as_src': 6850.0,
         'BBB:chkpt_yield': 1.8571428571428572, 'BBB:chkpt_apy': 547587.0028295065,
         'BBB:global_yield': 2.186046511627907, 'BBB:global_apy': 1150.9943403101925,
         'BBB:latest_cgt': 0.20,
         'BBB:chkpt_gain_src': 4500.0, 'BBB:chkpt_gain_net_src': 3600.0,
         'BBB:tot_gain_src': 4700.0, 'BBB:tot_gain_net_src': 3760.0,

         'chkpt_yield': 2.238095238095238, 'chkpt_apy': 2646126.1510352483,
         'global_yield': 1.9722222222222223, 'global_apy': 753.9376784192543},
    ]},
    {'in': {
        'AAA': _data_invstts[0]['out'],
        'BBB': [x for x in _data_invstts[1]['out']
                if x['datetime'] <= dt(2020, 2, 12, tzinfo=tz.utc)],
    }, 'out': [
        {'datetime': dt(2020, 1, 12, tzinfo=tz.utc),
         'diff_days': 0, 'tot_days': 0,

         'diff_src': 1000, 'tot_src': 1000, 'tot_dst_as_src': 1000.0,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0.0, 'tot_gain_net_src': 0.0,

         'AAA:diff_days': 0, 'AAA:tot_days': 0,
         'AAA:diff_src': 500, 'AAA:diff_dst': 5.0, 'AAA:latest_rate': 100,
         'AAA:tot_src': 500, 'AAA:tot_dst': 5.0, 'AAA:avg_rate': 100.0,
         'AAA:tot_dst_as_src': 500.0,
         'AAA:chkpt_yield': 0, 'AAA:chkpt_apy': 0,
         'AAA:global_yield': 0.0, 'AAA:global_apy': 0,
         'AAA:latest_cgt': 0,
         'AAA:chkpt_gain_src': 0, 'AAA:chkpt_gain_net_src': 0,
         'AAA:tot_gain_src': 0.0, 'AAA:tot_gain_net_src': 0.0,

         'BBB:diff_days': 0, 'BBB:tot_days': 0,
         'BBB:diff_src': 500, 'BBB:diff_dst': 10.0, 'BBB:latest_rate': 50,
         'BBB:tot_src': 500, 'BBB:tot_dst': 10.0, 'BBB:avg_rate': 50.0,
         'BBB:tot_dst_as_src': 500.0,
         'BBB:chkpt_yield': 0, 'BBB:chkpt_apy': 0,
         'BBB:global_yield': 0.0, 'BBB:global_apy': 0,
         'BBB:latest_cgt': 0,
         'BBB:chkpt_gain_src': 0, 'BBB:chkpt_gain_net_src': 0,
         'BBB:tot_gain_src': 0.0, 'BBB:tot_gain_net_src': 0.0,

         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0.0, 'global_apy': 0},

        {'datetime': dt(2020, 2, 12, tzinfo=tz.utc),
         'diff_days': 31.0, 'tot_days': 31.0,

         'diff_src': 2100, 'tot_src': 3100, 'tot_dst_as_src': 3150.0,
         'chkpt_gain_src': 50.0, 'chkpt_gain_net_src': 32.5,
         'tot_gain_src': 50.0, 'tot_gain_net_src': 32.5,

         'AAA:diff_days': 31.0, 'AAA:tot_days': 31.0,
         'AAA:diff_src': 700, 'AAA:diff_dst': 10.0, 'AAA:latest_rate': 70,
         'AAA:tot_src': 1200, 'AAA:tot_dst': 15.0, 'AAA:avg_rate': 80.0,
         'AAA:tot_dst_as_src': 1050.0,
         'AAA:chkpt_yield': -0.30000000000000004, 'AAA:chkpt_apy': -0.9849978210304741,
         'AAA:global_yield': -0.125, 'AAA:global_apy': -0.7924170918049609,
         'AAA:latest_cgt': 0.15,
         'AAA:chkpt_gain_src': -150.0, 'AAA:chkpt_gain_net_src': -127.5,
         'AAA:tot_gain_src': -150.0, 'AAA:tot_gain_net_src': -127.5,

         'BBB:diff_days': 31.0, 'BBB:tot_days': 31.0,
         'BBB:diff_src': 1400, 'BBB:diff_dst': 20.0, 'BBB:latest_rate': 70,
         'BBB:tot_src': 1900, 'BBB:tot_dst': 30.0, 'BBB:avg_rate': 63.333333333333336,
         'BBB:tot_dst_as_src': 2100.0,
         'BBB:chkpt_yield': 0.3999999999999999, 'BBB:chkpt_apy': 51.546013724696195,
         'BBB:global_yield': 0.10526315789473673, 'BBB:global_apy': 2.249177905018738,
         'BBB:latest_cgt': 0.20,
         'BBB:chkpt_gain_src': 200.0, 'BBB:chkpt_gain_net_src': 160.0,
         'BBB:tot_gain_src': 200.0, 'BBB:tot_gain_net_src': 160.0,

         'chkpt_yield': 0.05, 'chkpt_apy': 0.7761797254076475,
         'global_yield': 0.016129032258064516, 'global_apy': 0.20730561938737058},

        {'datetime': dt(2020, 3, 12, tzinfo=tz.utc),
         'diff_days': 29.0, 'tot_days': 60.0,

         'diff_src': 250, 'tot_src': 3350, 'tot_dst_as_src': 5950.0,
         'chkpt_gain_src': 2550.0, 'chkpt_gain_net_src': 2167.5,
         'tot_gain_src': 2600.0, 'tot_gain_net_src': 2200.0,

         'AAA:diff_days': 29.0, 'AAA:tot_days': 60.0,
         'AAA:diff_src': 250, 'AAA:diff_dst': 4.25, 'AAA:latest_rate': 200,
         'AAA:tot_src': 1450, 'AAA:tot_dst': 19.25, 'AAA:avg_rate': 75.32467532467533,
         'AAA:tot_dst_as_src': 3850.0,
         'AAA:chkpt_yield': 1.8571428571428572, 'AAA:chkpt_apy': 547587.0028295065,
         'AAA:global_yield': 1.6551724137931032, 'AAA:global_apy': 379.0996102191754,
         'AAA:latest_cgt': 0.15,
         'AAA:chkpt_gain_src': 2550.0, 'AAA:chkpt_gain_net_src': 2167.5,
         'AAA:tot_gain_src': 2400.0, 'AAA:tot_gain_net_src': 2040.0,

         'BBB:diff_days': None, 'BBB:tot_days': None,
         'BBB:diff_src': None, 'BBB:diff_dst': None, 'BBB:latest_rate': None,
         'BBB:tot_src': None, 'BBB:tot_dst': None, 'BBB:avg_rate': None,
         'BBB:tot_dst_as_src': None,
         'BBB:chkpt_yield': None, 'BBB:chkpt_apy': None,
         'BBB:global_yield': None, 'BBB:global_apy': None,
         'BBB:latest_cgt': None,
         'BBB:chkpt_gain_src': None, 'BBB:chkpt_gain_net_src': None,
         'BBB:tot_gain_src': None, 'BBB:tot_gain_net_src': None,

         'chkpt_yield': 0.8095238095238095, 'chkpt_apy': 1743.8479705869902,
         'global_yield': 0.7761194029850746, 'global_apy': 31.93231787318252},
    ]},
]


@pytest.fixture
def get_data_invsttsaggr():
    def factory(id: int = -1, side: str = ''):
        if id < 0:
            return deepcopy(_data_invsttsaggr)
        if side == '':
            return deepcopy(_data_invsttsaggr[id])
        return deepcopy(_data_invsttsaggr[id][side])

    return factory
