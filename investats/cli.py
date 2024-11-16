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


def load_data(file: TextIO, skip_check: bool = False) -> list[dict]:
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

        # TODO check that are sorted, if the bool param allows to do that
        # TODO make a flag out of the bool param

    return data


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

    # TODO flags to format the values with format strings (see apycalc)

    args = parser.parse_args(argv[1:])

    ############################################################################

    # TODO

    return 0
