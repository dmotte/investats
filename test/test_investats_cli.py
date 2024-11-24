#!/usr/bin/env python3

import io
import textwrap

from datetime import datetime as dt

from investats import load_data


def test_load_data():
    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12, type: chkpt }
        - { datetime: 2020-03-12, type: invest, inv_src: *inv, rate: 101.2731 }
        - { datetime: 2020-03-12, type: chkpt }
        - { datetime: 2020-04-12, type: invest, inv_src: *inv, rate: 101.9373 }
        - { datetime: 2020-04-12, type: chkpt }
        - { datetime: 2020-05-12, type: invest, inv_src: *inv, rate: 102.5841 }
        - { datetime: 2020-05-12, type: chkpt }
    ''')

    data = load_data(io.StringIO(yml))

    assert data[0]['datetime'] == dt(2020, 1, 12).astimezone()
