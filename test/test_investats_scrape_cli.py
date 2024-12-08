#!/usr/bin/env python3

import io
import textwrap

import pytest

from datetime import datetime as dt
from datetime import timezone as tz

from investats_scrape import is_txn_valid, load_data, save_data


def test_is_txn_valid():
    assert is_txn_valid({'datetime': '', 'asset': '', 'rate': '',
                         'inv_src': ''})
    assert is_txn_valid({'datetime': '', 'asset': '', 'rate': '',
                         'inv_dst': ''})
    assert is_txn_valid({'datetime': '', 'asset': '', 'rate': '',
                         'inv_src': '', 'some_other_field': ''})
    assert is_txn_valid({'datetime': '', 'asset': '', 'rate': '',
                         'inv_dst': '', 'some_other_field': ''})

    assert not is_txn_valid({})

    assert not is_txn_valid({'datetime': '', 'asset': '', 'rate': ''})
    assert not is_txn_valid({'datetime': '', 'asset': '', 'rate': '',
                             'inv_src': '', 'inv_dst': ''})

    assert not is_txn_valid({'datetime': '', 'rate': '', 'inv_src': ''})
    assert not is_txn_valid({'datetime': '', 'rate': '', 'inv_dst': ''})


def test_load_data():
    txt = textwrap.dedent('''\
        This is a sample list of transactions

        ########## TRANSACTION ##########

        Datetime:  2020-09-12T11:30:00Z
        Asset:     BBB
        Price:     25.0000
        Shares:    25

        ########## TRANSACTION ##########

        Datetime:  2020-10-12T12:00:00Z
        Asset:     AAA
        Price:     125.0000
        Shares:    22

        ########## TRANSACTION ##########

        Datetime:  2020-10-12T12:30:00Z
        Asset:     BBB
        Price:     20.0000
        Amount:    400.00

        ########## TRANSACTION ##########

        Datetime:  2020-11-12T14:00:00Z
        Asset:     AAA
        Price:     130.0000
        Amount:    2080.00

        ########## TRANSACTION ##########

        Datetime:  2020-11-12T14:30:00Z
        Asset:     BBB
        Price:     25.0000
        Shares:    15
    ''')

    data_out_expected = [
        {'datetime': dt(2020, 9, 12, 11, 30, tzinfo=tz.utc), 'asset': 'BBB',
         'rate': '25.0000', 'inv_dst': '25'},
        {'datetime': dt(2020, 10, 12, 12, tzinfo=tz.utc), 'asset': 'AAA',
         'rate': '125.0000', 'inv_dst': '22'},
        {'datetime': dt(2020, 10, 12, 12, 30, tzinfo=tz.utc), 'asset': 'BBB',
         'rate': '20.0000', 'inv_src': '400.00'},
        {'datetime': dt(2020, 11, 12, 14, tzinfo=tz.utc), 'asset': 'AAA',
         'rate': '130.0000', 'inv_src': '2080.00'},
        {'datetime': dt(2020, 11, 12, 14, 30, tzinfo=tz.utc), 'asset': 'BBB',
         'rate': '25.0000', 'inv_dst': '15'},
    ]

    data = list(load_data(io.StringIO(txt), '#####', 'Datetime:', 'Asset:',
                          'Amount:', 'Shares:', 'Price:'))
    assert data == data_out_expected

    txt += textwrap.dedent('''\
        ########## TRANSACTION ##########
    ''')

    data = list(load_data(io.StringIO(txt), '#####', 'Datetime:', 'Asset:',
                          'Amount:', 'Shares:', 'Price:'))
    assert data == data_out_expected

    with pytest.raises(ValueError, match=r'Invalid transaction: {.+}'):
        list(load_data(io.StringIO(txt), '#####', 'Datetime:', 'Asset:',
                       'Amount:', 'Shares:', 'ThisIsAWrongPrefix:'))


def test_save_data():
    data = [
        {'a': 'something', 'b': 123},
        {'a': 'something else', 'b': 456.789},
        {'datetime': dt(2020, 1, 1, tzinfo=tz.utc), 'foo': 'bar'},
        {'datetime': dt(2020, 1, 1, 1, 2, 3, tzinfo=tz.utc), 'x': 'foo',
         'y': 'baz'},
    ]

    yml = textwrap.dedent('''\
        ---
        - { a: something, b: 123 }
        - { a: something else, b: 456.789 }
        - { datetime: 2020-01-01 00:00:00+00:00, foo: bar }
        - { datetime: 2020-01-01 01:02:03+00:00, x: foo, y: baz }
    ''')

    buf = io.StringIO()
    save_data(data, buf)
    buf.seek(0)

    assert buf.read() == yml


def test_txns_to_entries():
    pass  # TODO
