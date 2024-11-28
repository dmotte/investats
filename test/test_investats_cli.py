#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import datetime as dt

from investats import load_data, complete_invest_entry, compute_stats


def test_load_data():
    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    data = load_data(io.StringIO(yml))

    assert data == [
        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 100},
        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'chkpt',
         'cgt': 0.15},
        {'datetime': dt(2020, 2, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 100.6558},
        {'datetime': dt(2020, 2, 12, 1, 23, 45).astimezone(), 'type': 'chkpt'},
    ]

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: foo, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError):  # Invalid entry type: foo
        load_data(io.StringIO(yml))

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: foo, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError):  # Invalid datetime type: foo
        load_data(io.StringIO(yml))

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558, inv_dst: 1234 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError):  # Invalid entry (inv_src + rate + inv_dst)
        load_data(io.StringIO(yml))

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError):  # Invalid entry (only inv_src is present)
        load_data(io.StringIO(yml))

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-11, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    # Invalid entry order: 2020-01-12 > 2020-01-11
    with pytest.raises(ValueError):
        load_data(io.StringIO(yml))

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-01-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    # Invalid entry order: 2020-01-12 >= 2020-01-12
    with pytest.raises(ValueError):
        load_data(io.StringIO(yml))


def test_complete_invest_entry():
    assert complete_invest_entry({'inv_dst': 100, 'rate': 3}) == \
        {'inv_src': 300, 'inv_dst': 100, 'rate': 3}
    assert complete_invest_entry({'inv_src': 100, 'rate': 8}) == \
        {'inv_src': 100, 'inv_dst': 12.5, 'rate': 8}
    assert complete_invest_entry({'inv_src': 100, 'inv_dst': 20}) == \
        {'inv_src': 100, 'inv_dst': 20, 'rate': 5}


def test_compute_stats():
    data_in = [
        {'datetime': dt(2020, 1, 1).astimezone(), 'type': 'chkpt',
         'notes': 'First checkpoint'},

        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 100},
        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'chkpt',
         'cgt': 0.15},

        {'datetime': dt(2020, 2, 12).astimezone(), 'type': 'invest',
         'inv_src': 700, 'rate': 70},
        {'datetime': dt(2020, 2, 12).astimezone(), 'type': 'chkpt'},

        {'datetime': dt(2020, 3, 10).astimezone(), 'type': 'invest',
         'inv_src': 200, 'rate': 50, 'notes': 'Some notes here'},
        {'datetime': dt(2020, 3, 12).astimezone(), 'type': 'invest',
         'inv_src': 50, 'rate': 200},
        {'datetime': dt(2020, 3, 12).astimezone(), 'type': 'chkpt'},
    ]

    data_out = list(compute_stats(data_in))

    assert data_out == [
        {'datetime': dt(2020, 1, 1).astimezone(),
         'diff_days': 0, 'tot_days': 0,
         'diff_src': 0, 'diff_dst': 0, 'latest_rate': 0,
         'tot_src': 0, 'tot_dst': 0, 'avg_rate': 0,
         'tot_dst_as_src': 0,
         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0, 'global_apy': 0,
         'latest_cgt': 0,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0, 'tot_gain_net_src': 0},
        {'datetime': dt(2020, 1, 12).astimezone(),
         'diff_days': 11, 'tot_days': 11,
         'diff_src': 500, 'diff_dst': 5, 'latest_rate': 100,
         'tot_src': 500, 'tot_dst': 5, 'avg_rate': 100,
         'tot_dst_as_src': 500,
         'chkpt_yield': 0, 'chkpt_apy': 0,
         'global_yield': 0, 'global_apy': 0,
         'latest_cgt': 0.15,
         'chkpt_gain_src': 0, 'chkpt_gain_net_src': 0,
         'tot_gain_src': 0, 'tot_gain_net_src': 0},
        {'datetime': dt(2020, 2, 12).astimezone(),
         'diff_days': 31, 'tot_days': 42,
         'diff_src': 700, 'diff_dst': 10, 'latest_rate': 70,
         'tot_src': 1200, 'tot_dst': 15, 'avg_rate': 80,
         'tot_dst_as_src': 1050,
         'chkpt_yield': -0.30000000000000004, 'chkpt_apy': -0.9849978210304741,
         'global_yield': -0.125, 'global_apy': -0.6866552911749941,
         'latest_cgt': 0.15,
         'chkpt_gain_src': -150, 'chkpt_gain_net_src': -127.5,
         'tot_gain_src': -150, 'tot_gain_net_src': -127.5},
        {'datetime': dt(2020, 3, 12).astimezone(),
         'diff_days': 29, 'tot_days': 71,
         'diff_src': 250, 'diff_dst': 4.25, 'latest_rate': 200,
         'tot_src': 1450, 'tot_dst': 19.25, 'avg_rate': 75.32467532467533,
         'tot_dst_as_src': 3850,
         'chkpt_yield': 1.8571428571428572, 'chkpt_apy': 547587.0028295065,
         'global_yield': 1.6551724137931032, 'global_apy': 150.42410185614494,
         'latest_cgt': 0.15,
         'chkpt_gain_src': 2550, 'chkpt_gain_net_src': 2167.5,
         'tot_gain_src': 2400, 'tot_gain_net_src': 2040},
    ]

    # TODO
