#!/apps/python/2.7.3/bin/python

import argparse
from verilog_util import *
from pyverilog_parser import *
import re

def get_port_size(port_name):
  m = re.findall("(.*)\[(.*)\]", port_name)
  if(len(m) == 0):
    port_size = 0
  else:
    (port_name, port_size) = m[0]
  
  return(port_name, int(port_size) + 1) # since the port are 0 based

def get_def_port_list(def_file):
  m = re.findall(".*PINS[\W+](.+?)[\W+];\n(.*)END PINS", def_file, re.DOTALL|re.MULTILINE)

  (def_num_pins, pin_list_str) = m[0]
  pin_list = pin_list_str.split('- ')
  print "Number of DEF pins : " + str(def_num_pins)
  port_list = {}
  del pin_list[0]

  for pin in pin_list:
    pin_info = pin.split('+')
    name = pin_info[0].strip()
    try:
      type = pin_info[2].split(' ')[2].strip().lower()
    except:
      print pin_info
      print pin_info[2]
      print pin_info[2].split(' ')
      print pin_info[2].split(' ')[2]
      print pin_info[2].split(' ')[2].strip()

    (name,size) = get_port_size(name)
    if name in port_list:
      if size > port_list[name]['size']:
        port_list[name]['size'] = size
    else:
      port_list[name] = {'size':size, 'type':type}

  return (def_num_pins, port_list)

def get_lef_port_list(lef_file):
  pin_list = lef_file.split('PIN')
  port_list = {}
  del pin_list[0]  # Remove header info

  for pin in pin_list:
    pin_info = pin.split(';')

    name = pin_info[0].split()[0].strip()
    type = pin_info[0].split()[2].strip().lower()
    (name,size) = get_port_size(name)
    if name in port_list:
      if size > port_list[name]['size']:
        port_list[name]['size'] = size
    else:
      port_list[name] = {'size':size, 'type':type}


  lef_num_pins = len(port_list)
  print "Number of LEF pins : " + str(lef_num_pins)
  return (lef_num_pins, port_list)


if __name__ == "__main__":  

  commandLine = argparse.ArgumentParser(description='Compares the def file to RTL for pins names, size and direction',
                                   usage='%(prog)s -def <path to def file>.def -rtl <path to toplevel rtl or blackbox>.v')
  commandLine.add_argument('-def', '--def_file', default=None)
  commandLine.add_argument('-lef', '--lef_file', default=None)
  commandLine.add_argument('-rtl', default=None)

  opt = commandLine.parse_args()

  if(opt.rtl == None):
    raise NameError("Must have valid rtl file")
  if(opt.def_file == None and opt.lef_file == None):
    raise NameError("Must have valid lef or def file")

  # Get the port list from the RTL
  f_rtl = open(opt.rtl)
  (mod_name, rtl_ports) = get_verilog_port_list(f_rtl.read())
  rtl_num_pins =0;
  rtl_num_pins = sum(map(lambda x: x['size'], rtl_ports))
  print "RTL Number of pins : " + str(rtl_num_pins)

  if(opt.def_file != None):
    # Get the pins from the DEF
    f_def = open(opt.def_file)
    (lefdef_num_pins, lefdef_ports) = get_def_port_list(f_def.read())
    file_type = "DEF"
  else:
    # Get the pins from the LEF
    f_lef = open(opt.lef_file)
    (lefdef_num_pins, lefdef_ports) = get_lef_port_list(f_lef.read())
    file_type = "LEF"
  
  if int(lefdef_num_pins) != int(rtl_num_pins):
    print "ERROR: Different number of pins: {}={} RTL={}".format(file_type, lefdef_num_pins,rtl_num_pins)

  # Compare the RTL to DEF port list
  for rtl_port in rtl_ports:
    if (rtl_port['name'] in lefdef_ports):
      # Check size/direction
      if(rtl_port['size'] != lefdef_ports[rtl_port['name']]['size']):
        print "ERROR: {} has different sizes between {} ({}) and RTL ({})".format(rtl_port['name'], file_type, lefdef_ports[rtl_port['name']]['size'], rtl_port['size'])
      if(rtl_port['type'] != lefdef_ports[rtl_port['name']]['type']):
        print "ERROR: {} has different direction between {} ({}) and RTL ({})".format(rtl_port['name'], file_type, lefdef_ports[rtl_port['name']]['type'], rtl_port['type'])
      del lefdef_ports[rtl_port['name']]
    else:
      print "ERROR: {} missing {}".format(file_type, rtl_port['name'])
 
  for lefdef_port in lefdef_ports:
    print "ERROR: {} Port not in the RTL : {}".format(file_type, lefdef_port)
  
