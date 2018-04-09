import datetime
from string import Template


raise DeprecationWarning("Should now use verilog_util.py")

def range_to_num_bits(range):
  if type(range) is int:
    return range

  if(range == ''):
    return 1

  range = range[1:]
  range = range[:-1]
  high = range.split(':')[0]
  low = range.split(':')[1]
  return int(high) - int(low) + 1

def find_port(name, port_list):
  # Check for capitalisation errors
  for port in port_list:
    if ((port.name != name) & (port.name.lower() == name.lower())):
      print port.name,
      print name
      raise NameError("Port names only differ by capitalisation : {} - {}".format(port.name, name))

  for port in port_list:
    if port.name == name:
      return True
  return False

def remove_port_from_list(port_name, port_list):
  for p in port_list:
    if (p['name'] == port_name):
      port_list.remove(p)
      return

  raise NameError("Tried to remove a port from list that isn't in the list: " + port_name)


def create_copyright_header():
  """
  Returns a string with the ICM tags and a creation date embedded.
  """

  disp_str = '//-----------------------------------------------------------------------------\n\
// Company    : u-blox Cork, Ireland\n\
// Created    : ${DATE}\n\
// Last commit: $$Date:$$\n\
// Updated by : $$Author:$$\n\
//-----------------------------------------------------------------------------\n\
// Copyright (c) ${YEAR} u-blox Cork, Ireland\n\
//-----------------------------------------------------------------------------\n\
// $$Id:$$\n\
// AUTO-GENERATED: Do Not Hand Edit\n\
//-----------------------------------------------------------------------------\n\n'

  t = Template(disp_str)

  return t.substitute(DATE=datetime.datetime.now().strftime("%A, %d %B %Y %I:%M%p"), \
  YEAR=datetime.datetime.now().strftime("%Y"))

