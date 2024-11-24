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
        if not entry['type'] in ['invest', 'chkpt']:
            raise ValueError('Invalid entry type: ' + str(entry['type']))

        if not isinstance(entry['datetime'], dt):
            if not isinstance(entry['datetime'], date):
                raise ValueError('Invalid datetime type: ' +
                                 str(entry['datetime']))

            entry['datetime'] = dt.combine(entry['datetime'], dt.min.time())

        if not is_aware(entry['datetime']):
            entry['datetime'] = entry['datetime'].astimezone()

        if entry['type'] == 'invest' and not any([
            'inv_src' not in entry and 'inv_dst' in entry and 'rate' in entry,
            'inv_src' in entry and 'inv_dst' not in entry and 'rate' in entry,
            'inv_src' in entry and 'inv_dst' in entry and 'rate' not in entry,
        ]):
            raise ValueError('Invalid entry ' + str(entry) + ': exactly two '
                             'values among "inv_src", "inv_dst" and "rate" '
                             'must be provided for each entry of '
                             'type "invest"')

    if check_sorted:
        for i in range(1, len(data)):
            prev, curr = data[i - 1], data[i]

            if prev['type'] == 'invest' and curr['type'] == 'chkpt':
                if prev['datetime'] > curr['datetime']:
                    raise ValueError('Invalid entry order: ' +
                                     str(prev['datetime']) + ' > ' +
                                     str(curr['datetime']))
            else:
                if prev['datetime'] >= curr['datetime']:
                    raise ValueError('Invalid entry order: ' +
                                     str(prev['datetime']) + ' >= ' +
                                     str(curr['datetime']))

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

    # TODO flags to format the values with format strings (see apycalc)

    args = parser.parse_args(argv[1:])

    ############################################################################

    def lambda_read(file: TextIO):
        return load_data(file, not args.skip_check_sorted)

    if args.file_in == '-':
        data_in = lambda_read(sys.stdin)
    else:
        with open(args.file_in, 'r') as f:
            data_in = lambda_read(f)

    data_out = compute_stats(data_in)

    def lambda_write(data: list[dict], file: TextIO):
        return save_data(data, file)

    if args.file_out == '-':
        lambda_write(data_out, sys.stdout)
    else:
        with open(args.file_out, 'w') as f:
            lambda_write(data_out, f)

    return 0
