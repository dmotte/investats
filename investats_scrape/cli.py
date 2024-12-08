#!/usr/bin/env python3

import argparse
import sys

from contextlib import ExitStack
from datetime import datetime as dt
from datetime import timedelta
from dateutil import parser as dup
from typing import TextIO


def is_txn_valid(txn: dict) -> bool:
    '''
    Checks whether a transaction is valid or not
    '''
    return all(k in txn for k in ['datetime', 'asset', 'rate']) \
        and ('inv_src' in txn) != ('inv_dst' in txn)


def load_data(file: TextIO, pfix_reset: str, pfix_datetime: str,
              pfix_asset: str, pfix_inv_src: str, pfix_inv_dst: str,
              pfix_rate: str):
    '''
    Scrapes transactions from a raw text file
    '''
    txn = {}

    for line in file:
        line = line.strip()

        if line.startswith(pfix_reset):
            if txn == {}:
                continue
            if not is_txn_valid(txn):
                raise ValueError('Invalid transaction: ' + str(txn))
            yield txn
            txn = {}
        elif line.startswith(pfix_datetime):
            txn['datetime'] = dup.parse(line.removeprefix(pfix_datetime))
        elif line.startswith(pfix_asset):
            txn['asset'] = line.removeprefix(pfix_asset).strip()
        elif line.startswith(pfix_inv_src):
            txn['inv_src'] = line.removeprefix(pfix_inv_src).strip()
        elif line.startswith(pfix_inv_dst):
            txn['inv_dst'] = line.removeprefix(pfix_inv_dst).strip()
        elif line.startswith(pfix_rate):
            txn['rate'] = line.removeprefix(pfix_rate).strip()

    if not is_txn_valid(txn):
        raise ValueError('Invalid transaction: ' + str(txn))
    yield txn


def save_data(data: list[dict], file: TextIO):
    '''
    Saves data into a YAML file
    '''
    print('---', file=file)

    for entry in data:
        print('- { ' + ', '.join([
            f'{k}: {str(v)}' for k, v in entry.items()
        ]) + ' }', file=file)


def txns_to_entries(txns: list[dict], asset: str, cgt: float = 0):
    '''
    Filters transactions related to a specific asset, and converts them to
    investats-compatible entries
    '''
    is_first_chkpt = True
    prev_txn = None

    for txn in txns:
        if txn['asset'] != asset:
            continue

        if prev_txn is not None \
                and txn['datetime'].date() != prev_txn['datetime'].date():
            chkpt = {
                'datetime': dt.combine(
                    (prev_txn['datetime'] + timedelta(days=1)).date(),
                    dt.min.time(), prev_txn['datetime'].tzinfo,
                ),
                'type': 'chkpt',
            }

            if is_first_chkpt:
                if cgt != 0:
                    chkpt['cgt'] = cgt
                is_first_chkpt = False

            yield chkpt

        yield {'datetime': txn['datetime'], 'type': 'invest'} | \
            {k: txn[k] for k in ['inv_src', 'inv_dst', 'rate'] if k in txn}

        prev_txn = txn

    # TODO add the last checkpoint! For example, I could use enumerate and
    # move the checks on the next entry instead of the previous


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Scrape input data for investats from raw text'
    )

    parser.add_argument('file_in', metavar='FILE_IN', type=str,
                        nargs='?', default='-',
                        help='Input file. If set to "-" then stdin is used '
                        '(default: -)')
    parser.add_argument('file_out', metavar='FILE_OUT', type=str,
                        nargs='?', default='-',
                        help='Output file. If set to "-" then stdout is used '
                        '(default: -)')

    # TODO flags

    args = parser.parse_args(argv[1:])

    ############################################################################

    with ExitStack() as stack:
        file_in = (sys.stdin if args.file_in == '-'
                   else stack.enter_context(open(args.file_in, 'r')))
        file_out = (sys.stdout if args.file_out == '-'
                    else stack.enter_context(open(args.file_out, 'w')))

        # TODO make the params customizable, with flags, of course
        txns = load_data(file_in, '###', 'Datetime:', 'Asset:',
                         'Amount:', 'Shares:', 'Price:')
        entries = txns_to_entries(txns, 'AAA', 0.15)
        save_data(entries, file_out)

    return 0
