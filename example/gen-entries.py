#!/usr/bin/env python3

import argparse
import sys

from datetime import date
from datetime import timedelta
from enum import StrEnum


class Freq(StrEnum):
    '''
    Represents how often an investment is made
    '''
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'

    # TODO unit tests
    # TODO consider to have this script as a subcommand
    def next(self, d: date) -> date:
        '''
        Calculates the date of the next investment
        '''
        match self:
            case Freq.DAILY:
                return d + timedelta(days=1)
            case Freq.WEEKLY:
                return d + timedelta(weeks=1)
            case Freq.MONTHLY:
                return d.replace(month=d.month + 1)
            case Freq.YEARLY:
                return d.replace(year=d.year + 1)


def generate_entries(date_start: date, init_src: float, rate: float,
                     apy: float, freq: Freq, count: int, cgt: float):
    '''
    Generates entries based on some parameters
    '''
    # TODO d = Freq.prev(date_start) ???

    for i in range(count):
        entry = {}

        yield entry


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Generate sample entries based on some parameters'
    )

    # TODO flags

    args = parser.parse_args(argv[1:])

    ############################################################################

    # TODO entries=...

    # TODO write entries to args.file_out

    return 0


if __name__ == '__main__':
    sys.exit(main())
