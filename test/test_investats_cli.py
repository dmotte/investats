#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import datetime as dt

from investats import load_data


def test_load_data():
    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    data = load_data(io.StringIO(yml))

    assert data[0]['datetime'] == dt(2020, 1, 12).astimezone()
    assert data[0]['type'] == 'invest'
    assert data[0]['inv_src'] == 500
    assert data[0]['rate'] == 100
    assert 'inv_dst' not in data[0]

    assert data[1]['datetime'] == dt(2020, 1, 12).astimezone()
    assert data[1]['type'] == 'chkpt'
    assert data[1]['cgt'] == 0.15

    assert data[2]['datetime'] == dt(2020, 2, 12).astimezone()
    assert data[2]['type'] == 'invest'
    assert data[2]['inv_src'] == 500
    assert data[2]['rate'] == 100.6558
    assert 'inv_dst' not in data[2]

    assert data[3]['datetime'] == dt(2020, 2, 12, 1, 23, 45).astimezone()
    assert data[3]['type'] == 'chkpt'
    assert 'cgt' not in data[3]

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
