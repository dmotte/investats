#!/usr/bin/env python3

import argparse
import csv
import sys

from collections.abc import Callable, Iterator
from dateutil import parser as dup
from typing import Any, TextIO


def pair_items_to_dict(items: list[str]) -> dict[str, str]:
    '''
    Converts a list of (asset name, input file) pairs, specified as a simple
    array of items, to a Python dictionary
    '''
    len_items = len(items)

    if len_items % 2 != 0:
        raise ValueError('The length of pair items must be an even number')
    if len_items < 4:
        raise ValueError('The number of pairs must be >= 2')

    return {items[i]: items[i + 1] for i in range(0, len_items, 2)}


def load_data(file: TextIO) -> Iterator[dict[str, Any]]:
    '''
    Loads data from a CSV file
    '''
    data = list(csv.DictReader(file))

    float_keys = [k for k in data[0].keys() if k != 'datetime']

    for x in data:
        yield {'datetime': dup.parse(x['datetime'])} | \
            {k: float(x[k]) for k in float_keys}


def save_data(data: list[dict], file: TextIO, fmt_days: str = '',
              fmt_src: str = '', fmt_dst: str = '', fmt_rate: str = '',
              fmt_yield: str = '') -> None:
    '''
    Saves data into a CSV file
    '''
    func_days = str if fmt_days == '' else lambda x: fmt_days.format(x)
    func_src = str if fmt_src == '' else lambda x: fmt_src.format(x)
    func_dst = str if fmt_dst == '' else lambda x: fmt_dst.format(x)
    func_rate = str if fmt_rate == '' else lambda x: fmt_rate.format(x)
    func_yield = str if fmt_yield == '' else lambda x: fmt_yield.format(x)

    def get_fmt(key: str) -> Callable[[Any], str]:
        '''
        Determines the format function for a specific field key
        '''
        if key == 'datetime' or key.endswith(':latest_cgt'):
            return str

        if key in ('diff_days', 'tot_days') \
                or key.endswith((':diff_days', ':tot_days')):
            return func_days

        if key in ('diff_src', 'tot_src', 'tot_dst_as_src',
                   'chkpt_gain_src', 'chkpt_gain_net_src',
                   'tot_gain_src', 'tot_gain_net_src') \
            or key.endswith((':diff_src', ':tot_src', ':tot_dst_as_src',
                             ':chkpt_gain_src', ':chkpt_gain_net_src',
                             ':tot_gain_src', ':tot_gain_net_src')):
            return func_src

        if key.endswith((':diff_dst', ':tot_dst')):
            return func_dst

        if key.endswith((':latest_rate', ':avg_rate')):
            return func_rate

        if key in ('chkpt_yield', 'chkpt_apy',
                   'global_yield', 'global_apy') \
            or key.endswith((':chkpt_yield', ':chkpt_apy',
                            ':global_yield', ':global_apy')):
            return func_yield

        raise ValueError(f'Unsupported key: {key}')

    fields = {k: get_fmt(k) for k in data[0].keys()}

    print(','.join(fields.keys()), file=file)
    for x in data:
        print(','.join('' if x[k] is None else f(x[k])
                       for k, f in fields.items()), file=file)


def aggregate_series(
        named_series: dict[str, list[dict]]) -> Iterator[dict[str, Any]]:
    '''
    Aggregates multiple investats data series into a single one
    '''
    if len(named_series) < 2:
        raise ValueError('The number of series must be >= 2')

    # Keys of the input fields for which the values from the series must be
    # summed, in the correct order for output
    KEYS_SUM_ORDERED = ('diff_src', 'tot_src', 'tot_dst_as_src',
                        'chkpt_gain_src', 'chkpt_gain_net_src',
                        'tot_gain_src', 'tot_gain_net_src')
    # Keys of the input fields for which the values from the series must be
    # summed, and missing values must be considered zero
    KEYS_SUM_DEF_ZERO = ('diff_src',
                         'chkpt_gain_src', 'chkpt_gain_net_src')
    # Keys of the input fields for which the values from the series must be
    # summed, and missing values must be considered equal to the previous entry
    # if any, or zero if there is no previous entry (i.e. the series has
    # not started yet)
    keys_sum_def_prev = [k for k in KEYS_SUM_ORDERED
                         if k not in KEYS_SUM_DEF_ZERO]

    keys_specific = [k for k in next(iter(named_series.values()))[0].keys()
                     if k != 'datetime']

    ############################################################################

    iterators = {name: iter(series) for name, series in named_series.items()}

    # Entries preceding the ones in curr_entries.
    # If an entry is missing in this dict, it basically means the related
    # series has not started yet
    prev_entries = {}
    # This dict always contains the entries related to the iterators positions.
    # If an entry is missing in this dict, it basically means the related
    # series has ended
    curr_entries = {}
    for name, it in iterators.items():
        try:
            curr_entries[name] = next(it)
        except StopIteration:
            pass

    prev_aggr = None

    while len(curr_entries) > 0:
        min_dt = min(e['datetime'] for e in curr_entries.values())

        if prev_aggr is not None and prev_aggr['datetime'] >= min_dt:
            raise ValueError('Invalid entry order: ' +
                             str(prev_aggr['datetime']) + ' >= ' + str(min_dt))

        # This dict contains only the entries related to the
        # current datetime (min_dt)
        named_entries = {name: entry for name, entry in curr_entries.items()
                         if entry['datetime'] == min_dt}

        aggr = {'datetime': min_dt}  # Aggregated (output) entry

        ########################################################################

        # We compute the days fields using the same formulas as
        # the "investats" module
        if prev_aggr is None:
            aggr['diff_days'] = 0
            aggr['tot_days'] = 0
        else:
            aggr['diff_days'] = (
                min_dt - prev_aggr['datetime']
            ).total_seconds() / 60 / 60 / 24
            aggr['tot_days'] = prev_aggr['tot_days'] + aggr['diff_days']

        ########################################################################

        aggr |= {k: sum(named_entries[name][k] if name in named_entries
                        else prev_entries[name][k] if name in prev_entries
                        else 0
                        for name in named_series.keys())
                 if k in keys_sum_def_prev
                 else sum(e[k] for e in named_entries.values())
                 for k in KEYS_SUM_ORDERED} | \
                {f'{name}:{k}': named_entries[name][k] if name in named_entries
                 else None
                 for name in named_series.keys() for k in keys_specific}

        ########################################################################

        # We calculate the "aggregate yields" using the following alternative
        # (but equivalent) formulas

        aggr['chkpt_yield'] = 0 if prev_aggr is None \
            or prev_aggr['tot_dst_as_src'] == 0 \
            else aggr['chkpt_gain_src'] / prev_aggr['tot_dst_as_src']

        aggr['chkpt_apy'] = 0 if aggr['chkpt_yield'] == 0 \
            or aggr['diff_days'] == 0 \
            else (1 + aggr['chkpt_yield']) ** (365 / aggr['diff_days']) - 1

        aggr['global_yield'] = 0 if aggr['tot_src'] == 0 \
            else aggr['tot_gain_src'] / aggr['tot_src']

        aggr['global_apy'] = 0 if aggr['global_yield'] == 0 \
            or aggr['tot_days'] == 0 \
            else (1 + aggr['global_yield']) ** (365 / aggr['tot_days']) - 1

        ########################################################################

        yield aggr

        prev_aggr = aggr

        for name, entry in named_entries.items():
            prev_entries[name] = entry
            try:
                curr_entries[name] = next(iterators[name])
            except StopIteration:
                del curr_entries[name]


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Aggregate multiple investats data series into a single one'
    )

    parser.add_argument('pairs', metavar='PAIRS', type=str, nargs='+',
                        help='List of (asset name, input file) pairs, as '
                        'array of items (e.g. AAA stats-aaa.csv '
                        'BBB stats-bbb.csv)')

    parser.add_argument('--fmt-days', type=str, default='',
                        help='If specified, formats the days values with this '
                        'format string (e.g. "{:.2f}")')
    parser.add_argument('--fmt-src', type=str, default='',
                        help='If specified, formats the SRC values with this '
                        'format string (e.g. "{:.2f}")')
    parser.add_argument('--fmt-dst', type=str, default='',
                        help='If specified, formats the DST values with this '
                        'format string (e.g. "{:.4f}")')
    parser.add_argument('--fmt-rate', type=str, default='',
                        help='If specified, formats the rate values with this '
                        'format string (e.g. "{:.6f}")')
    parser.add_argument('--fmt-yield', type=str, default='',
                        help='If specified, formats the yield values with this '
                        'format string (e.g. "{:.4f}")')

    args = parser.parse_args(argv[1:])

    ############################################################################

    named_series = {}

    for name, file in pair_items_to_dict(args.pairs).items():
        with open(file, 'r') as f:
            named_series[name] = list(load_data(f))

    save_data(list(aggregate_series(named_series)), sys.stdout, args.fmt_days,
              args.fmt_src, args.fmt_dst, args.fmt_rate, args.fmt_yield)

    return 0
