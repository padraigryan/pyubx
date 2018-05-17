#!/usr/bin/env python

import argparse
import vcd.utils as utils


if __name__ == "__main__":
    # Check for the right version of python
    commandLine = argparse.ArgumentParser(description='Set of VCD editing utils',
                                          usage='%(prog)s [options] <vcd_file_name>')
    commandLine.add_argument('-c', '--crop',
                             help='Include this segment, -c <start> <end> or <start> <+/-offset> (in fs)',
                             nargs=2,
                             action='append')
    commandLine.add_argument('-t', '--trim',
                             help='Trim time off the beginning or end <+/-offset> (in fs)',
                             nargs=1,
                             action='store')
    commandLine.add_argument('-s', '--shift',
                             help='Trim time off the beginning or end <+/-offset> (in fs)',
                             nargs=1,
                             action='store')
    commandLine.add_argument('-apb', '--apb_decode',
                             help='A VCD with APB signals will be decoded into read/write pairs',
                             action='store_true',
                             default=False)
    commandLine.add_argument('-ahb', '--ahb_decode',
                             help='A VCD with AHB signals will be decoded into read/write pairs',
                             action='store_true',
                             default=False)
    commandLine.add_argument('vcd_file_name',
                             help='VCD file to edit',
                             action='store')

    opt = commandLine.parse_args()

