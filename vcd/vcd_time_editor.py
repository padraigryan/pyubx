#!/usr/bin/env python

import argparse
import sys
import vcd_utils


def active_line_callback(signals, timestamp):
    pass

if __name__ == "__main__":  
  # Check for the right version of python
  if sys.version_info < (2, 7):
    raise "ERROR: Use python version 2.7 or greater"

  commandLine = argparse.ArgumentParser(description='Single step firmware/simulation tool for AMS VCD generation',
                                   usage='%(prog)s [options] <test case name>')
  commandLine.add_argument('-c', '--crop',        help='Include this segment, -c <start> <end> or <start> <+/-offset> (in fs)', nargs=2, action='append')
  commandLine.add_argument('-t', '--trim',        help='Trim time off the beginning or end <+/-offset> (in fs)', nargs=1, action='store')
  commandLine.add_argument('-s', '--shift',        help='Trim time off the beginning or end <+/-offset> (in fs)', nargs=1, action='store')
  commandLine.add_argument('vcd_file_name',       help='Source VCD file to edit', action='store')

  opt = commandLine.parse_args()

#  vcd_in = vcd_utils.vcd_file(opt.vcd_file_name)
#  vcd_in.parse_vcd_vars(active_line_callback);

#  vcd_out = vcd_utils.vcd_file(opt.vcd_file_name.split('.') [0] + "_short.vcd")

  # Perform the signal shift
  fh = open(opt.vcd_file_name, "r")
  fh.seek(0)
  sig_decl = True 
  sig_chng = False
  sig_shift = True
  
  time_shift = int(opt.shift[0])

  for line in fh.readlines():
    line = line.strip()
    if(sig_decl):
      print line
      if(line.startswith("$enddefinitions")):
        sig_chng = True
        sig_decl = False
    elif(sig_chng):
      if(sig_shift):
        if(line.startswith('#')):
          print '#' + str(int(line[1:]) - time_shift) 
        else:
          print line
      elif( (line.startswith('#')) and (int(line[1:]) >= time_shift) ):
        sig_shift = True

  fh.close()
