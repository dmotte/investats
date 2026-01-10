#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import datetime as dt
from datetime import timezone as tz

from investats import load_data, save_data, complete_invest_entry, compute_stats

from util import pfmt


def test_load_data() -> None:
    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    data = load_data(io.StringIO(yml))

    assert pfmt(data) == pfmt([
        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 100.0},
        {'datetime': dt(2020, 1, 12).astimezone(), 'type': 'chkpt',
         'cgt': 0.15},
        {'datetime': dt(2020, 2, 12).astimezone(), 'type': 'invest',
         'inv_src': 500, 'rate': 100.6558},
        {'datetime': dt(2020, 2, 12, 1, 23, 45).astimezone(), 'type': 'chkpt'},
    ])

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: 500, rate: 100 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError) as exc_info:
        load_data(io.StringIO(yml))
    assert exc_info.value.args == ('The first entry must be of type "invest"',)

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: foo, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError) as exc_info:
        load_data(io.StringIO(yml))
    assert exc_info.value.args == ('Invalid entry type: foo',)

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: foo, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError) as exc_info:
        load_data(io.StringIO(yml))
    assert exc_info.value.args == ('Invalid datetime type: foo',)

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv, rate: 100.6558, inv_dst: 1234 }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError, match=r'Invalid entry {.+}: exactly two '
                       r'values among "inv_src", "inv_dst" and "rate" must be '
                       r'provided for each entry of type "invest"'):
        load_data(io.StringIO(yml))

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12, type: invest, inv_src: *inv }
        - { datetime: 2020-02-12 01:23:45, type: chkpt }
    ''')

    with pytest.raises(ValueError, match=r'Invalid entry {.+}: exactly two '
                       r'values among "inv_src", "inv_dst" and "rate" must be '
                       r'provided for each entry of type "invest"'):
        load_data(io.StringIO(yml))

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12 00:00:00+00:00, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-11 00:00:00+00:00, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-02-12 00:00:00+00:00, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45+00:00, type: chkpt }
    ''')

    with pytest.raises(ValueError) as exc_info:
        load_data(io.StringIO(yml))
    assert exc_info.value.args == (
        'Invalid entry order: 2020-01-12 00:00:00+00:00 > '
        '2020-01-11 00:00:00+00:00',)

    yml = textwrap.dedent('''\
        ---
        - { datetime: 2020-01-12 00:00:00+00:00, type: invest, inv_src: &inv 500, rate: 100.0000 }
        - { datetime: 2020-01-12 00:00:00+00:00, type: chkpt, cgt: 0.15 }
        - { datetime: 2020-01-12 00:00:00+00:00, type: invest, inv_src: *inv, rate: 100.6558 }
        - { datetime: 2020-02-12 01:23:45+00:00, type: chkpt }
    ''')

    with pytest.raises(ValueError) as exc_info:
        load_data(io.StringIO(yml))
    assert exc_info.value.args == (
        'Invalid entry order: 2020-01-12 00:00:00+00:00 >= '
        '2020-01-12 00:00:00+00:00',)


def test_save_data(get_data_invstts) -> None:
    data = get_data_invstts(0, 'out')

    headers_line = (
        'datetime,diff_days,tot_days,diff_src,diff_dst,latest_rate,tot_src,'
        'tot_dst,avg_rate,tot_dst_as_src,chkpt_yield,chkpt_apy,global_yield,'
        'global_apy,latest_cgt,chkpt_gain_src,chkpt_gain_net_src,tot_gain_src,'
        'tot_gain_net_src')

    csv = '\n'.join((
        headers_line,
        '2020-01-12 00:00:00+00:00,0,0,500,5,100,500,5,100,500,0,0,0,0,0,'
        '0,0,0,0',
        '2020-02-12 00:00:00+00:00,31,31,700,10,70,1200,15,80,1050,'
        '-0.30000000000000004,-0.9849978210304741,-0.125,-0.7924170918049609,'
        '0.15,-150,-127.5,-150,-127.5',
        '2020-03-12 00:00:00+00:00,29,60,250,4.25,200,1450,19.25,'
        '75.32467532467533,3850,1.8571428571428572,547587.0028295065,'
        '1.6551724137931032,379.0996102191754,0.15,2550,2167.5,2400,2040',
    )) + '\n'

    buf = io.StringIO()
    save_data(data, buf)
    buf.seek(0)

    assert buf.read() == csv

    csv = '\n'.join((
        headers_line,
        '2020-01-12 00:00:00+00:00,0.00,0.00,500.000,5.0000,100.00000,'
        '500.000,5.0000,100.00000,500.000,0.000000,0.000000,0.000000,'
        '0.000000,0,0.000,0.000,0.000,0.000',
        '2020-02-12 00:00:00+00:00,31.00,31.00,700.000,10.0000,70.00000,'
        '1200.000,15.0000,80.00000,1050.000,-0.300000,-0.984998,-0.125000,'
        '-0.792417,0.15,-150.000,-127.500,-150.000,-127.500',
        '2020-03-12 00:00:00+00:00,29.00,60.00,250.000,4.2500,200.00000,'
        '1450.000,19.2500,75.32468,3850.000,1.857143,547587.002830,1.655172,'
        '379.099610,0.15,2550.000,2167.500,2400.000,2040.000',
    )) + '\n'

    buf = io.StringIO()
    save_data(data, buf, '{:.2f}', '{:.3f}', '{:.4f}', '{:.5f}', '{:.6f}')
    buf.seek(0)

    assert buf.read() == csv


def test_complete_invest_entry() -> None:
    assert complete_invest_entry({'inv_dst': 100, 'rate': 3}) == \
        {'inv_src': 300, 'inv_dst': 100, 'rate': 3}
    assert complete_invest_entry({'inv_src': 100, 'rate': 8}) == \
        {'inv_src': 100, 'inv_dst': 12.5, 'rate': 8}
    assert complete_invest_entry({'inv_src': 100, 'inv_dst': 20}) == \
        {'inv_src': 100, 'inv_dst': 20, 'rate': 5}

    assert complete_invest_entry({'inv_dst': 0, 'rate': 3}) == \
        {'inv_src': 0, 'inv_dst': 0, 'rate': 3}
    assert complete_invest_entry({'inv_dst': 100, 'rate': 0}) == \
        {'inv_src': 0, 'inv_dst': 100, 'rate': 0}

    assert complete_invest_entry({'inv_src': 0, 'rate': 8}) == \
        {'inv_src': 0, 'inv_dst': 0, 'rate': 8}
    assert complete_invest_entry({'inv_src': 100, 'rate': 0}) == \
        {'inv_src': 100, 'inv_dst': 0, 'rate': 0}

    assert complete_invest_entry({'inv_src': 0, 'inv_dst': 20}) == \
        {'inv_src': 0, 'inv_dst': 20, 'rate': 0}
    assert complete_invest_entry({'inv_src': 100, 'inv_dst': 0}) == \
        {'inv_src': 100, 'inv_dst': 0, 'rate': 0}

    with pytest.raises(KeyError) as exc_info:
        complete_invest_entry({'inv_src': 0})
    assert exc_info.value.args == ('rate',)

    with pytest.raises(KeyError) as exc_info:
        complete_invest_entry({'inv_dst': 0})
    assert exc_info.value.args == ('rate',)

    with pytest.raises(KeyError) as exc_info:
        complete_invest_entry({'rate': 0})
    assert exc_info.value.args == ('inv_dst',)


def test_compute_stats(get_data_invstts) -> None:
    for pair in get_data_invstts():
        data_in = pair['in']
        data_in_copy = [x.copy() for x in data_in]
        data_out_expected = pair['out']
        data_out_actual = list(compute_stats(data_in))
        assert pfmt(data_in) == pfmt(data_in_copy)
        assert pfmt(data_out_actual) == pfmt(data_out_expected)

    data_in = get_data_invstts(0, 'in')
    data_in[0]['datetime'] = dt(2020, 1, 1, tzinfo=tz.utc)
    data_in_copy = [x.copy() for x in data_in]
    data_out_expected = get_data_invstts(0, 'out')
    data_out_actual = list(compute_stats(data_in))
    assert pfmt(data_in) == pfmt(data_in_copy)
    assert pfmt(data_out_actual) == pfmt(data_out_expected)
