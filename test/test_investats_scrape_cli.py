#!/usr/bin/env python3

import textwrap

from investats_scrape import is_txn_valid


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


def test_TODO():
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

    pass  # TODO
