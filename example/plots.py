#!/usr/bin/env python3

import argparse
import csv
import sys

from dateutil import parser as dup
from typing import TextIO

import plotly.express as px


def load_data(file: TextIO):
    '''
    Loads data from a CSV file
    '''
    data = list(csv.DictReader(file))

    for x in data:
        iterator = iter(x.items())

        k, v = next(iterator)
        if k != 'datetime':
            raise ValueError('The first field is not "datetime"')
        x[k] = dup.parse(v)

        for k, v in iterator:
            x[k] = float(v)

        yield x


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Generate plots based on data computed with investats and '
        'aggregated with investats_aggr'
    )

    parser.add_argument('file_in', metavar='FILE_IN', type=str,
                        nargs='?', default='-',
                        help='Input file. If set to "-" then stdin is used '
                        '(default: -)')

    parser.add_argument('-t', '--plot-tdas', action='store_true',
                        help='Generate plot based on tot_dst_as_src values')
    parser.add_argument('-r', '--plot-rate', action='store_true',
                        help='Generate plot based on rate values')
    parser.add_argument('-a', '--plot-apy', action='store_true',
                        help='Generate plot based on APY values')

    args = parser.parse_args(argv[1:])

    ############################################################################

    if args.file_in == '-':
        data = load_data(sys.stdin)
    else:
        with open(args.file_in, 'r') as f:
            data = load_data(f)

    data = list(data)

    if args.plot_tdas:
        # TODO
        fig.show()

    if args.plot_rate:
        # TODO
        fig.show()

    if args.plot_apy:
        # TODO
        fig.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
