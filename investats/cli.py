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


def load_data(file: TextIO) -> list[dict]:
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


def complete_invest_entry(entry_in: dict) -> dict:
    '''
    Complete an entry of type "invest" with the missing fields that can be
    calculated from the others
    '''
    entry_out = entry_in.copy()

    if 'inv_src' not in entry_out:
        entry_out['inv_src'] = entry_out['inv_dst'] * entry_out['rate']
    elif 'inv_dst' not in entry_out:
        entry_out['inv_dst'] = entry_out['inv_src'] / entry_out['rate']
    elif 'rate' not in entry_out:
        entry_out['rate'] = entry_out['inv_src'] / entry_out['inv_dst']

    return entry_out


def compute_stats(data: list[dict]):
    '''
    Computes the statistics
    '''
    data = [x.copy() for x in data]

    prev_out = None

    diff_src, diff_dst, latest_rate = 0, 0, 0

    for entry_in in data:
        if entry_in['type'] == 'invest':
            entry_in = complete_invest_entry(entry_in)

            diff_src += entry_in['inv_src']
            diff_dst += entry_in['inv_dst']
            latest_rate = entry_in['rate']
        elif entry_in['type'] == 'chkpt':
            entry_out = {'datetime': entry_in['datetime']}

            # - diff_days: how many days have passed since the last checkpoint
            # - tot_days: how many days have passed since the first checkpoint

            if prev_out is None:
                entry_out['diff_days'] = 0
                entry_out['tot_days'] = 0
            else:
                entry_out['diff_days'] = (
                    entry_out['datetime'] - prev_out['datetime']
                ).total_seconds() / 60 / 60 / 24
                entry_out['tot_days'] = prev_out['tot_days'] + \
                    entry_out['diff_days']

            # - diff_src: invested SRC since the last checkpoint
            # - diff_dst: invested DST since the last checkpoint
            # - latest_rate: latest SRC/DST rate (at the latest operation)

            entry_out['diff_src'], entry_out['diff_dst'] = diff_src, diff_dst
            entry_out['latest_rate'] = latest_rate

            # - tot_src: total invested SRC
            # - tot_dst: total invested DST
            # - avg_rate: ratio between tot_src and tot_dst

            if prev_out is None:
                entry_out['tot_src'] = diff_src
                entry_out['tot_dst'] = diff_dst
            else:
                entry_out['tot_src'] = prev_out['tot_src'] + diff_src
                entry_out['tot_dst'] = prev_out['tot_dst'] + diff_dst

            entry_out['avg_rate'] = 0 if entry_out['tot_dst'] == 0 \
                else entry_out['tot_src'] / entry_out['tot_dst']

            # - tot_dst_as_src: how many SRC would be obtained by converting
            #   tot_dst using latest_rate

            entry_out['tot_dst_as_src'] = entry_out['tot_dst'] * latest_rate

            # - chkpt_yield: yield w.r.t. the last checkpoint
            # - chkpt_apy: APY w.r.t. the last checkpoint

            if prev_out is None or prev_out['latest_rate'] == 0:
                entry_out['chkpt_yield'] = 0
                entry_out['chkpt_apy'] = 0
            else:
                entry_out['chkpt_yield'] = \
                    latest_rate / prev_out['latest_rate'] - 1
                entry_out['chkpt_apy'] = (1 + entry_out['chkpt_yield']) ** (
                    365 / entry_out['diff_days']) - 1

            # - global_yield: yield w.r.t. avg_rate
            # - global_apy: APY w.r.t. avg_rate

            # TODO implementation

            # - latest_cgt: latest CGT (Capital Gains Tax)

            # TODO implementation

            # - chkpt_gain_src: gain w.r.t. the last checkpoint
            # - chkpt_gain_net_src: net gain w.r.t. the last checkpoint

            # TODO implementation

            # - tot_gain_src: gain w.r.t. tot_src
            # - tot_gain_net_src: net gain w.r.t. tot_src

            # TODO implementation

            diff_src, diff_dst = 0, 0

            prev_out = entry_out

            yield entry_out
        else:
            raise ValueError('Invalid entry type: ' + str(entry_in['type']))


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

    # TODO flags to format the values with format strings (see apycalc)

    args = parser.parse_args(argv[1:])

    ############################################################################

    def lambda_read(file: TextIO):
        return load_data(file)

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
