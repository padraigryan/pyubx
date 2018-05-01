#!/home/prya/usr/bin/python

import argparse


def declare_signals(module_name, ports):
  # Declare the signals
  disp_str = "\n  // " + module_name + "\n"
  for port in ports:
    if(port["type"] == "localparam"):
      continue
    else:
      disp_str = disp_str + "  wire {0:44}{1};\n".format(port["size"],  port["name"])

  return disp_str

###############################################################################
# Connect in the same order as declared in the module
def instance_module_style1(module_name, ports):

  # Instance the module
  disp_str = "\n{0} {0} (\n".format(module_name)

  first_pin = True;
  for port in ports:
    if(port["type"] != "localparam"):
      if(first_pin == False):
        disp_str = disp_str + "),\n"
      first_pin = False;

      disp_str = disp_str + "    .{0:42}({0}".format(port["name"])
  disp_str = disp_str + ")\n  );\n"
  return disp_str

###############################################################################
# Connect with inputs/outputs grouped together
def instance_module_style2(module_name, ports):

  # Instance the module
  disp_str = "  {0} {0} (\n".format(module_name)

  first_pin = True;
  disp_str = disp_str + "    // Inputs\n"
  for port in ports:
    if((port["type"] != "localparam") & (port["type"] == "input")):
      if(first_pin == False):
         disp_str = disp_str + "),\n"
      first_pin = False;

      disp_str = disp_str + "    .{0:42}({0}".format(port["name"])

  disp_str = disp_str + "),\n\n    // Outputs\n"

  first_pin = True;
  for port in ports:
    if( (port["type"] != "localparam") & (port["type"] == "output") ):
      if(first_pin == False):
        disp_str = disp_str + "),\n"
      first_pin = False;
      disp_str = disp_str + "    .{0:42}({0}".format(port["name"])

  disp_str = disp_str + ")\n  );\n"
  return disp_str

###############################################################################
# Connect according the names provided. Ports is assumed to have a list of 
# tuples containing the port name and the signal to connect it to.
# Intended to be called from another python scripts
def instance_module_style3(module_name, ports):

  # Instance the module
  disp_str = "\n{0} {0} (\n".format(module_name)

  first_pin = True;
  for (port, sig) in ports:
    if(first_pin == False):
      disp_str = disp_str + "),\n"
    first_pin = False;

    disp_str = disp_str + "    .{0:42}({1}".format(port, sig)
  disp_str = disp_str + ")\n  );\n"

  return disp_str

###############################################################################
# Connect straight through as with style 1 and 2, but if the port is listed in the
# exceptions listed, connect to signal supplied.
# Intended to be called from another python scripts
def instance_module_style4(module_name, ports, connection_exceptions):

  # Instance the module
  disp_str = "\n{0} {0} (\n".format(module_name)

  first_pin = True;

  for port in ports:
    excpt_caught = False;
    if(port["type"] != "localparam"):
      if(first_pin == False):
        disp_str = disp_str + "),\n"
      first_pin = False;
      
      # Check for a connection exception
      for (port_name, wire_name) in connection_exceptions:
        if(port["name"] == port_name):
          disp_str = disp_str + "    .{0:42}({1}".format(port_name, wire_name)
          excpt_caught = True

      # Otherwise connect straight thru    
      if(excpt_caught == False):
        disp_str = disp_str + "    .{0:42}({0}".format(port["name"])

  disp_str = disp_str + ")\n  );\n"
  return disp_str

###############################################################################
# Instance VHDL module
def instance_module_style5(module_name, ports):

  # Instance the module
  disp_str = "\n{0} : {0} port map (\n".format(module_name)

  for port in ports:
    disp_str = disp_str + "    {0:42} => {0},".format(port['name']) + '\n'
  disp_str = disp_str[:-1]
  disp_str = disp_str + "\n  );\n"
  
  return disp_str
###############################################################################
# Just instance the default way.
def instance_module(fn):
    f = open(fn)

    if(fn.split(".")[-1] == "vhd"):
      (mn, p) = get_vhdl_port_list(f.read())
    else:
      (mn, p) = get_verilog_port_list(f.read())

    return instance_module_style1(mn, p)

if __name__ == "__main__":  

  commandLine = argparse.ArgumentParser(description='Instance modules from a source verilog/VHDL file',
                                   usage='%(prog)s [option|@optFile]... verilog/VHDL file')
  commandLine.add_argument('-g',  '--group',   help='The IOs are grouped as inputs and outputs', action='store_true', default = False)
  commandLine.add_argument('-d',  '--declare', help='Declare the wires needed for hookup', action='store_true', default = False)
  commandLine.add_argument('-v',  '--vhdl',    help='Instance as VHDL', action='store_true', default = False)
  commandLine.add_argument('file_name',        help='Source file to instance (verilog or VHDL)')

  opt = commandLine.parse_args()

  f = open(opt.file_name)

  if( (opt.file_name.split(".")[-1] == "vhd") | 
      (opt.file_name.split(".")[-1] == "vhdl") ):
    (mn, p) = get_vhdl_port_list(f.read())
  else:
    (mn, p) = get_verilog_port_list(f.read())

  if opt.declare:
    print declare_signals(mn, p)

  if opt.group:
    print instance_module_style2(mn, p)
  elif(opt.vhdl):
    print instance_module_style5(mn, p)
  else:
    print instance_module_style1(mn, p)


