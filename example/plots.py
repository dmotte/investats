#!/usr/bin/env python3

import argparse
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='TODO'
    )

    # TODO

    args = parser.parse_args(argv[1:])

    ############################################################################

    # TODO

    return 0


if __name__ == '__main__':
    sys.exit(main())
