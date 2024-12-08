#!/usr/bin/env python3

import argparse
import csv
import sys

from contextlib import ExitStack
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

    parser.add_argument('-s', '--plot-src', action='store_true',
                        help='Generate plot based on SRC values')
    parser.add_argument('-r', '--plot-rate', action='store_true',
                        help='Generate plot based on rate values')
    parser.add_argument('-g', '--plot-gain', action='store_true',
                        help='Generate plot based on gain values')
    parser.add_argument('-a', '--plot-apy', action='store_true',
                        help='Generate plot based on APY values')

    args = parser.parse_args(argv[1:])

    ############################################################################

    with ExitStack() as stack:
        file_in = (sys.stdin if args.file_in == '-'
                   else stack.enter_context(open(args.file_in, 'r')))
        data = list(load_data(file_in))

    if args.plot_src:
        fig = px.line(
            data,
            x='datetime',
            y=[k for k in data[0].keys()
               if k in ['tot_src', 'tot_dst_as_src']
               or k.endswith((':tot_src', ':tot_dst_as_src'))],
            template='plotly_dark',
            title='SRC values',

            hover_name='datetime',
            hover_data=['tot_days'],
            markers=True,
        )
        fig.show()

    if args.plot_rate:
        fig = px.line(
            data,
            x='datetime',
            y=[k for k in data[0].keys()
               if k.endswith((':latest_rate', ':avg_rate'))],
            template='plotly_dark',
            title='Rate values',

            hover_name='datetime',
            hover_data=['tot_days'],
            markers=True,
        )
        for k in data[0].keys():
            if not k.endswith(':avg_rate'):
                continue
            fig.add_hline(annotation_text=k, y=data[-1][k], line_color='#0c0')
        fig.show()

    if args.plot_gain:
        fig = px.line(
            data,
            x='datetime',
            y=[k for k in data[0].keys()
               if k in ['tot_gain_src', 'tot_gain_net_src']
               or k.endswith((':tot_gain_src', ':tot_gain_net_src'))],
            template='plotly_dark',
            title='Gain values',

            hover_name='datetime',
            hover_data=['tot_days'],
            markers=True,
        )
        fig.show()

    if args.plot_apy:
        fig = px.line(
            # The first entry is skipped, as APY is always zero there
            data[1:],
            x='datetime',
            y=[k for k in data[0].keys()
               if k == 'global_apy' or k.endswith(':global_apy')],
            template='plotly_dark',
            title='APY values',

            hover_name='datetime',
            hover_data=['tot_days'],
            markers=True,
        )
        fig.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())
