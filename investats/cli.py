#!/usr/bin/env python3

import argparse
import sys


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
