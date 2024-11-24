#!/usr/bin/env python3

import argparse
import sys

from datetime import date
from datetime import timedelta
from enum import Enum
from typing import TextIO


class Freq(str, Enum):
    '''
    Represents how often an investment is made
    '''
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'

    def prev(self, d: date) -> date:
        '''
        Calculates the date of the previous investment
        '''
        match self:
            case Freq.DAILY:
                return d - timedelta(days=1)
            case Freq.WEEKLY:
                return d - timedelta(weeks=1)
            case Freq.MONTHLY:
                return d.replace(year=d.year - 1, month=12) if d.month == 1 \
                    else d.replace(month=d.month - 1)
            case Freq.YEARLY:
                return d.replace(year=d.year - 1)

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
                return d.replace(year=d.year + 1, month=1) if d.month == 12 \
                    else d.replace(month=d.month + 1)
            case Freq.YEARLY:
                return d.replace(year=d.year + 1)


def generate_entries(file: TextIO, date_start: date, init_src: str,
                     init_rate: float, apy: float, freq: Freq, count: int,
                     cgt: str = '', fmt_rate: str = ''):
    '''
    Generates entries based on some parameters
    '''
    if count < 2:
        raise ValueError('Count should be >= 2')

    d = date_start
    rate = init_rate
    str_rate = str(rate) if fmt_rate == '' else fmt_rate.format(rate)

    print('---', file=file)
    print('- { datetime: %s, type: invest, inv_src: &inv %s, rate: %s }' %
          (d.strftime('%Y-%m-%d'), init_src, str_rate), file=file)
    print('- { datetime: %s, type: chkpt%s }' %
          (d.strftime('%Y-%m-%d'), '' if cgt == '' else f', cgt: {cgt}'),
          file=file)

    for _ in range(1, count):
        d = freq.next(d)
        days = (d - date_start).total_seconds() / 60 / 60 / 24
        rate = init_rate * (1 + apy) ** (days / 365)
        str_rate = str(rate) if fmt_rate == '' else fmt_rate.format(rate)

        print('- { datetime: %s, type: invest, inv_src: *inv, rate: %s }' %
              (d.strftime('%Y-%m-%d'), str_rate), file=file)
        print('- { datetime: %s, type: chkpt }' % d.strftime('%Y-%m-%d'),
              file=file)


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
