#!/usr/bin/env python3

import argparse
import logging
import sys
from .unused_deps_py_lib.processor import Processor


BAZEL_FLAGS = ["--tool_tag=unused_deps", "--keep_going", "--color=yes", "--curses=yes"]


def main():
    args = vars(parse_args())
    log_level = args.pop('log_level')
    logging.basicConfig(
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(message)s",
        level=getattr(logging, log_level)
    )
    instance = Processor(**args)
    instance.process()


def parse_args():
    parser = argparse.ArgumentParser(
        prog = "unused_deps_py",
        description='''Finds unused dependencies in Java targets

For Java rules in TARGETs, prints commands to delete deps unused at compile time.
Note these may be used at run time; see documentation for more information.
''')

    parser.add_argument(
        "--log-level",
        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
        default="INFO",
        help="Logging level",
    )

    parser.add_argument(
        "--workspace-path",
        required=True,
        action='store',
        help='Path to your workspace'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.0.5'
    )

    parser.add_argument(
        '--build-tool',
        action='store',
        default='bazel',
        help='the build executable (like bazel)'
    )

    parser.add_argument(
        '--extra-action-file',
        action='store',
        help='When specified, just prints suspected unused deps.'
    )

    parser.add_argument(
        '--output-file',
        action='store',
        help='used only with extra-action-file'
    )

    parser.add_argument(
        '--extra-build-flags',
        action='store',
        help='Extra build flags to use when building the targets.'
    )

    parser.add_argument('targets', metavar='TARGETS', nargs='*',
                        help='Bazel targets to analyze')

    return parser.parse_args()


if __name__ == '__main__':
    main()
