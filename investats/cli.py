#!/usr/bin/env python3

import argparse
import sys


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Investment statistics calculator'
    )

    # TODO

    args = parser.parse_args(argv[1:])

    ############################################################################

    # TODO

    return 0
