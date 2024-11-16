#!/usr/bin/env python3

import argparse
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Generate line plots based on TODO'
    )

    parser.add_argument('file_in', metavar='FILE_IN', type=str,
                        nargs='?', default='-',
                        help='Input file. If set to "-" then stdin is used '
                        '(default: -)')

    # TODO flags to enable/disable the generation of each plot (see apycalc)

    args = parser.parse_args(argv[1:])

    ############################################################################

    # TODO

    return 0


if __name__ == '__main__':
    sys.exit(main())
