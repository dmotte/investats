#!/usr/bin/env python3

import argparse
import sys

from datetime import datetime as dt
from datetime import date
from typing import TextIO

import yaml


def is_aware(d: dt):
    '''
    Returns true if the datetime object `d` is timezone-aware, false otherwise.
    See https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
    '''
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None


def load_data(file: TextIO, check_sorted: bool = True) -> list[dict]:
    '''
    Loads data from a YAML file
    '''
    data = yaml.safe_load(file)

    # YAML supports parsing dates out of the box if they are in the correct
    # format (ISO-8601). See
    # https://symfony.com/doc/current/components/yaml/yaml_format.html#dates

    for entry in data:
        if not isinstance(entry['datetime'], dt):
            if not isinstance(entry['datetime'], date):
                raise ValueError('Invalid datetime type: ' + entry['datetime'])

            entry['datetime'] = dt.combine(entry['datetime'], dt.min.time())

        if not is_aware(entry['datetime']):
            entry['datetime'] = entry['datetime'].astimezone()

    if check_sorted:
        for i in range(1, len(data)):
            dt_curr, dt_prev = data[i]['datetime'], data[i - 1]['datetime']
            if dt_curr <= dt_prev:
                raise ValueError('Datetime ' + str(dt_curr) +
                                 ' is <= than the previous one ' + str(dt_prev))

    return data


def save_data(data: list[dict], file: TextIO):
    '''
    Saves data into a CSV file
    '''
    data = [x.copy() for x in data]

    # TODO formats for the following categories (with sensible value in
    # parentheses, for the example):
    #   - fmt_days (2)
    #   - fmt_src (2)
    #   - fmt_dst (4) (common one, in case of multiple assets, in future version)
    #   - fmt_rate (6)
    #   - fmt_yield (4)

    # TODO better print (see apycalc)
    keys = list(data[0].keys())
    print(','.join(keys), file=file)
    for x in data:
        print(','.join(str(x[k]) if k in x else '-' for k in keys), file=file)


def compute_stats(data: list[dict]):
    '''
    Computes the statistics
    '''
    data = [x.copy() for x in data]

    for index, entry in enumerate(data):
        # TODO logic!
        entry['test'] = 100 + index

        yield entry


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Investment statistics calculator'
    )

    parser.add_argument('file_in', metavar='FILE_IN', type=str,
                        nargs='?', default='-',
                        help='Input file. If set to "-" then stdin is used '
                        '(default: -)')
    parser.add_argument('file_out', metavar='FILE_OUT', type=str,
                        nargs='?', default='-',
                        help='Output file. If set to "-" then stdout is used '
                        '(default: -)')

    # TODO make sure that you use all the defined args

    parser.add_argument('-s', '--skip-check-sorted', action='store_true',
                        help='If set, the input entries will not be checked '
                        'to be in ascending order')

    # TODO for the save_data function
    parser.add_argument('-n', '--notes', action='store_true',
                        help='If set, the note column will be included in '
                        'the output')

    # TODO flags to format the values with format strings (see apycalc)

    args = parser.parse_args(argv[1:])

    ############################################################################

    if args.file_in == '-':
        data_in = load_data(sys.stdin, not args.skip_check_sorted)
    else:
        with open(args.file_in, 'r') as f:
            data_in = load_data(f, not args.skip_check_sorted)

    data_out = compute_stats(data_in)

    if args.file_out == '-':
        save_data(data_out, sys.stdout)
    else:
        with open(args.file_out, 'w') as f:
            save_data(data_out, f)

    return 0
