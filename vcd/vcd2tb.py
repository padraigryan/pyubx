#!/usr/bin/env python

import argparse
import sys
sys.path.append("/hosted/projects2/prya/pyublx")
import verilog_util
import vcd_utils
import inst_mod
import datetime
import os

prev_time_step = 0

"""
TODO:
1) Smaller file size by putting all stim into a single reg and concat values
2) Check the outputs against the VCD block outputs
"""

# This is the handle for every line in the VCD
def add_vcd_stim(dut_inputs, timestamp):
  global prev_time_step
  cur_time_step = float(timestamp[:-2])
  delta_time = cur_time_step - prev_time_step 
  #print "{:10} {:10} {:10} {:10}".format(timestamp, prev_time_step, cur_time_step, delta_time)

  #print "\t//{}\n\t#{};".format( timestamp, str(delta_time))

  concat_sig = []
  for s in dut_inputs:
    if dut_inputs[s]['value'] == 'x':
      dut_inputs[s]['value'] = "'bx"
    concat_sig.append(dut_inputs[s]['value'])

  print "\t#{:10} vcd_vec = {:30}{:10}//{}".format(str(delta_time), '{'+", ".join(concat_sig)+'};', "", timestamp)
  prev_time_step = cur_time_step

if __name__ == "__main__":  
  # Check for the right version of python
  if sys.version_info < (2, 7):
    raise "ERROR: Use python version 2.7 or greater"

  commandLine = argparse.ArgumentParser(description='Create a block testbench using vcd as stimulus',
                                   usage='%(prog)s [options] <test case name>')
  commandLine.add_argument('-vcd', '--vcd_filename',       help='Source VCD to use for stimulus', action='store')

  opt = commandLine.parse_args()
   
  vcd = vcd_utils.vcd_file(opt.vcd_filename)
  # The required time unit, maybe different to the one used in the VCD, will scale it.
  vcd.timeunit='ns'

  # Write out the testbench to stdio
  print "module {}_tb; begin\n".format(opt.vcd_filename.split("/")[-1].split('.')[0])
  tot_vec_size = 0
  vcd_vec_sig = []
  for (s) in vcd.signals:
    signal = vcd.signals[s]
    print "wire [{}:0] {};".format(int(signal['size'])-1, signal['name'])
    tot_vec_size = tot_vec_size + signal['size']
    vcd_vec_sig.append(signal['name'])

  print "\nwire [{}:0] vcd_vec;".format(tot_vec_size-1)
  print "assign {" + ",".join(vcd_vec_sig) + "} = vcd_vec;\n"

  print "initial begin\n"
  print "// Source file is : {}".format(os.path.abspath(opt.vcd_filename))
  print "// Generated on : {}\n".format( datetime.datetime.now())
  vcd.parse_vcd_vars(add_vcd_stim)
  print "\t$finish;\n\tend\nend\nendmodule"

