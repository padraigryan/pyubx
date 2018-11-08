#!/usr/bin/env python

import argparse
import sys
from exceptions import KeyError

import utils

on = []
off = []
vcd_out = None
past_trim = False


def active_line_callback(signals, timestamp, vcd_line):
    global past_trim
    if vcd_line.startswith("#"):
        timestamp = int(vcd_line[1:])
        if timestamp > on[0]:
            past_trim = True
        vcd_line = "#" + str(timestamp - on[0]) + "\n"
    if past_trim:
        vcd_out.vcd_file_contents = vcd_out.vcd_file_contents + vcd_line
    print vcd_line,

if __name__ == "__main__":
    # Check for the right version of python
    if sys.version_info < (2, 7):
        raise "ERROR: Use python version 2.7 or greater"

    commandLine = argparse.ArgumentParser(description='Single step firmware/simulation tool for AMS VCD generation',
                                          usage='%(prog)s [options] <test case name>')
    commandLine.add_argument('-c', '--cut',
                             help='Revove this segment for all signals, -c <start> <end> or <start> <+/-offset> (in fs)',
                             nargs=2, action='append')
    commandLine.add_argument('-t', '--trim', help='Trim time off the beginning or end <+/-offset> (in fs)', nargs=1,
                             action='store')
    commandLine.add_argument('-s', '--shift', help='Move the waveforms backward <-offset> or foward <+offset>', nargs=1,
                             action='store')
    commandLine.add_argument('vcd_file_name', help='Source VCD file to edit', action='store')

    opt = commandLine.parse_args()

    opt.vcd_file_name = "../test/samples/vcd/simple.vcd"

    # Process the VCD file
    vcd_in = utils.VCDFile(opt.vcd_file_name)

    # Perform the signal shift
    try:
        scale = utils.k_timescales[opt.trim[0][-2:]]            # command line scale
        scale = int(utils.k_timescales[vcd_in.scale]/scale)     # Source vcd scale
        time_shift = int(opt.trim[0][0:-2]) * scale             # The trim in source vcd scale
    except KeyError:
        time_shift = int(opt.trim[0])
    if time_shift < 0:
        raise NotImplementedError

    off.append(0)
    on.append(time_shift)

    # Create the new file
    vcd_out = utils.VCDFile(opt.vcd_file_name.split('.')[0] + "_short.vcd", True)

    # Take the header directly from the source file.
    vcd_out.vcd_file_contents = vcd_in.read_vcd_header(True)

    # Process the source vcd line-by-line
    vcd_in.parse_vcd_vars(active_line_callback)

    vcd_out.export_vcd()

