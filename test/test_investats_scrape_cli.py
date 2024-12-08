#!/usr/bin/env python3

import textwrap


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
