#!/usr/bin/env python3

import argparse
import sys


def aggregate_series(series: list[list[dict]]):
    '''
    Aggregates multiple investats data series into a single one
    '''
    if len(series) < 2:
        raise ValueError('The number of series must be >= 2')

    pass  # TODO


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Aggregate multiple investats data series into a single one'
    )

    # TODO

    args = parser.parse_args(argv[1:])

    ############################################################################

    # TODO

    return 0
