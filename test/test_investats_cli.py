#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import datetime as dt

from investats import load_data, compute_stats


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


def test_compute_stats():
    data_in = [
        {'datetime': dt(2020, 1, 1).astimezone(), 'type': 'chkpt',
         'cgt': 0.15},

        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 100},
        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'chkpt'},

        {'datetime': dt(2020, 2, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 100.8128},
        {'datetime': dt(2020, 2, 12).astimezone(), 'type': 'chkpt'},

        {'datetime': dt(2020, 3, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 101.5526},
        {'datetime': dt(2020, 3, 12).astimezone(), 'type': 'chkpt'},
    ]

    data_out = list(compute_stats(data_in))

    assert data_out == [
        {'datetime': dt(2020, 1, 1).astimezone(),
         'diff_days': 0, 'tot_days': 0},
        {'datetime': dt(2020, 1, 12).astimezone(),
         'diff_days': 11, 'tot_days': 11},
        {'datetime': dt(2020, 2, 12).astimezone(),
         'diff_days': 31, 'tot_days': 42},
        {'datetime': dt(2020, 3, 12).astimezone(),
         'diff_days': 29, 'tot_days': 71},
    ]

    # TODO
