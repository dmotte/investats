#!/usr/bin/env python3

import io
import textwrap

import pytest

from copy import deepcopy
from datetime import datetime as dt
from datetime import timezone as tz

from investats_aggr import pair_items_to_dict, load_data, save_data, \
    aggregate_series

from util import pfmt


def test_pair_items_to_dict() -> None:
    assert pair_items_to_dict(['A', 'aaa', 'B', 'bbb']) == \
        {'A': 'aaa', 'B': 'bbb'}
    assert pair_items_to_dict(['A', 'aaa', 'B', 'bbb', 'C', 'ccc']) == \
        {'A': 'aaa', 'B': 'bbb', 'C': 'ccc'}

    with pytest.raises(ValueError) as exc_info:
        pair_items_to_dict(['A', 'aaa', 'B'])
    assert exc_info.value.args == (
        'The length of pair items must be an even number',)

    with pytest.raises(ValueError) as exc_info:
        pair_items_to_dict(['A', 'aaa'])
    assert exc_info.value.args == ('The number of pairs must be >= 2',)


def test_load_data() -> None:
    csv = textwrap.dedent('''\
        datetime,field01,field02,field03
        2020-01-01 00:00:00,0,0,0
        2020-01-12 00:00:00,11,11,500
        2020-02-12 00:00:00,31,42,700.123
        2020-03-12 00:00:00,29,71,250.001
    ''')

    data = list(load_data(io.StringIO(csv)))

    assert pfmt(data) == pfmt([
        {'datetime': dt(2020, 1, 1),
         'field01': 0.0, 'field02': 0.0, 'field03': 0.0},
        {'datetime': dt(2020, 1, 12),
         'field01': 11.0, 'field02': 11.0, 'field03': 500.0},
        {'datetime': dt(2020, 2, 12),
         'field01': 31.0, 'field02': 42.0, 'field03': 700.123},
        {'datetime': dt(2020, 3, 12),
         'field01': 29.0, 'field02': 71.0, 'field03': 250.001},
    ])


def test_save_data(get_data_invsttsaggr) -> None:
    data = get_data_invsttsaggr(0, 'out')

    headers_line = (
        'datetime,diff_days,tot_days,'
        'diff_src,tot_src,tot_dst_as_src,'
        'chkpt_gain_src,chkpt_gain_net_src,tot_gain_src,tot_gain_net_src,'
        'AAA:diff_days,AAA:tot_days,'
        'AAA:diff_src,AAA:diff_dst,AAA:latest_rate,'
        'AAA:tot_src,AAA:tot_dst,AAA:avg_rate,'
        'AAA:tot_dst_as_src,'
        'AAA:chkpt_yield,AAA:chkpt_apy,AAA:global_yield,AAA:global_apy,'
        'AAA:latest_cgt,'
        'AAA:chkpt_gain_src,AAA:chkpt_gain_net_src,'
        'AAA:tot_gain_src,AAA:tot_gain_net_src,'
        'BBB:diff_days,BBB:tot_days,'
        'BBB:diff_src,BBB:diff_dst,BBB:latest_rate,'
        'BBB:tot_src,BBB:tot_dst,BBB:avg_rate,'
        'BBB:tot_dst_as_src,'
        'BBB:chkpt_yield,BBB:chkpt_apy,BBB:global_yield,BBB:global_apy,'
        'BBB:latest_cgt,'
        'BBB:chkpt_gain_src,BBB:chkpt_gain_net_src,'
        'BBB:tot_gain_src,BBB:tot_gain_net_src,'
        'chkpt_yield,chkpt_apy,global_yield,global_apy')

    csv = '\n'.join((
        headers_line,
        #
        '2020-01-12 00:00:00+00:00,0,0,1000,1000,1000,0,0,0,0,'
        '0,0,500,5,100,500,5,100,500,0,0,0,0,0,0,0,0,0,'
        '0,0,500,10,50,500,10,50,500,0,0,0,0,0,0,0,0,0,'
        '0,0,0,0',
        #
        '2020-02-12 00:00:00+00:00,31,31,2100,3100,3150,50,32.5,50,32.5,'
        '31,31,700,10,70,1200,15,80,1050,-0.30000000000000004,-0.9849978210304741,-0.125,-0.7924170918049609,0.15,-150,-127.5,-150,-127.5,'
        '31,31,1400,20,70,1900,30,63.333333333333336,2100,0.3999999999999999,51.546013724696195,0.10526315789473673,2.249177905018738,0.2,200,160,200,160,'
        '0.05,0.7761797254076475,0.016129032258064516,0.20730561938737058',
        #
        '2020-03-12 00:00:00+00:00,29,60,500,3600,10700,7050,5767.5,7100,5800,'
        '29,60,250,4.25,200,1450,19.25,75.32467532467533,3850,1.8571428571428572,547587.0028295065,1.6551724137931032,379.0996102191754,0.15,2550,2167.5,2400,2040,'
        '29,60,250,4.25,200,2150,34.25,62.77372262773723,6850,1.8571428571428572,547587.0028295065,2.186046511627907,1150.9943403101925,0.2,4500,3600,4700,3760,'
        '2.238095238095238,2646126.1510352483,1.9722222222222223,753.9376784192543',
    )) + '\n'

    buf = io.StringIO()
    save_data(data, buf)
    buf.seek(0)

    assert buf.read() == csv

    csv = '\n'.join((
        headers_line,
        #
        '2020-01-12 00:00:00+00:00,0.00,0.00,1000.000,1000.000,1000.000,0.000,0.000,0.000,0.000,'
        '0.00,0.00,500.000,5.0000,100.00000,500.000,5.0000,100.00000,500.000,0.000000,0.000000,0.000000,0.000000,0,0.000,0.000,0.000,0.000,'
        '0.00,0.00,500.000,10.0000,50.00000,500.000,10.0000,50.00000,500.000,0.000000,0.000000,0.000000,0.000000,0,0.000,0.000,0.000,0.000,'
        '0.000000,0.000000,0.000000,0.000000',
        #
        '2020-02-12 00:00:00+00:00,31.00,31.00,2100.000,3100.000,3150.000,50.000,32.500,50.000,32.500,'
        '31.00,31.00,700.000,10.0000,70.00000,1200.000,15.0000,80.00000,1050.000,-0.300000,-0.984998,-0.125000,-0.792417,0.15,-150.000,-127.500,-150.000,-127.500,'
        '31.00,31.00,1400.000,20.0000,70.00000,1900.000,30.0000,63.33333,2100.000,0.400000,51.546014,0.105263,2.249178,0.2,200.000,160.000,200.000,160.000,'
        '0.050000,0.776180,0.016129,0.207306',
        #
        '2020-03-12 00:00:00+00:00,29.00,60.00,500.000,3600.000,10700.000,'
        '7050.000,5767.500,7100.000,5800.000,'
        '29.00,60.00,250.000,4.2500,200.00000,1450.000,19.2500,75.32468,3850.000,1.857143,547587.002830,1.655172,379.099610,0.15,2550.000,2167.500,2400.000,2040.000,'
        '29.00,60.00,250.000,4.2500,200.00000,2150.000,34.2500,62.77372,6850.000,1.857143,547587.002830,2.186047,1150.994340,0.2,4500.000,3600.000,4700.000,3760.000,'
        '2.238095,2646126.151035,1.972222,753.937678',
    )) + '\n'

    buf = io.StringIO()
    save_data(data, buf, '{:.2f}', '{:.3f}', '{:.4f}', '{:.5f}', '{:.6f}')
    buf.seek(0)

    assert buf.read() == csv

    ############################################################################

    data = get_data_invsttsaggr(1, 'out')

    csv = '\n'.join((
        headers_line,
        #
        '2020-01-12 00:00:00+00:00,0,0,1000,1000,1000,0,0,0,0,'
        '0,0,500,5,100,500,5,100,500,0,0,0,0,0,0,0,0,0,'
        '0,0,500,10,50,500,10,50,500,0,0,0,0,0,0,0,0,0,'
        '0,0,0,0',
        #
        '2020-02-12 00:00:00+00:00,31,31,2100,3100,3150,50,32.5,50,32.5,'
        '31,31,700,10,70,1200,15,80,1050,-0.30000000000000004,-0.9849978210304741,-0.125,-0.7924170918049609,0.15,-150,-127.5,-150,-127.5,'
        '31,31,1400,20,70,1900,30,63.333333333333336,2100,0.3999999999999999,51.546013724696195,0.10526315789473673,2.249177905018738,0.2,200,160,200,160,'
        '0.05,0.7761797254076475,0.016129032258064516,0.20730561938737058',
        #
        '2020-03-12 00:00:00+00:00,29,60,250,3350,5950,2550,2167.5,2600,2200,'
        '29,60,250,4.25,200,1450,19.25,75.32467532467533,3850,1.8571428571428572,547587.0028295065,1.6551724137931032,379.0996102191754,0.15,2550,2167.5,2400,2040,'
        ',,,,,,,,,,,,,,,,,,'
        '0.8095238095238095,1743.8479705869902,0.7761194029850746,31.93231787318252',
    )) + '\n'

    buf = io.StringIO()
    save_data(data, buf)
    buf.seek(0)

    assert buf.read() == csv

    ############################################################################

    data_bad = [{'datetime': 12345, 'asdfghjkl': 67890},
                {'datetime': 11223, 'asdfghjkl': 34455},
                {'datetime': 66778, 'asdfghjkl': 89900}]

    buf = io.StringIO()
    with pytest.raises(ValueError) as exc_info:
        save_data(data_bad, buf)
    assert exc_info.value.args == ('Unsupported key: asdfghjkl',)


def test_aggregate_series(get_data_invsttsaggr) -> None:
    for pair in get_data_invsttsaggr():
        data_in = pair['in']
        data_in_copy = deepcopy(data_in)
        data_out_expected = pair['out']
        data_out_actual = list(aggregate_series(data_in))
        assert pfmt(data_in) == pfmt(data_in_copy)
        assert pfmt(data_out_actual) == pfmt(data_out_expected)

    with pytest.raises(ValueError) as exc_info:
        list(aggregate_series({}))
    assert exc_info.value.args == ('The number of series must be >= 2',)

    data_in = get_data_invsttsaggr(0, 'in')
    data_in['BBB'][1]['datetime'] = dt(2020, 1, 11, tzinfo=tz.utc)
    data_in_copy = deepcopy(data_in)
    with pytest.raises(ValueError) as exc_info:
        list(aggregate_series(data_in))
    assert exc_info.value.args == (
        'Invalid entry order: 2020-01-12 00:00:00+00:00 >= '
        '2020-01-11 00:00:00+00:00',)
    assert pfmt(data_in) == pfmt(data_in_copy)

    data_in = get_data_invsttsaggr(0, 'in')
    data_in['BBB'][1]['datetime'] = dt(2020, 1, 12, tzinfo=tz.utc)
    data_in_copy = deepcopy(data_in)
    with pytest.raises(ValueError) as exc_info:
        list(aggregate_series(data_in))
    assert exc_info.value.args == (
        'Invalid entry order: 2020-01-12 00:00:00+00:00 >= '
        '2020-01-12 00:00:00+00:00',)
    assert pfmt(data_in) == pfmt(data_in_copy)
