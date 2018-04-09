#!/apps/python/2.7.3/bin/python

import argparse
from inst_mod import *
from verilog_util import *
from pyverilog_parser import *

def make_wrapper(mn, fn_list, bb=False, drive_0=False): 
  """
  Takes a list of file(s) to wrap into a single module.  Will create ports for 
  each unique port found in each sub-module. WARNING: This may not be what you want.
  If it's a black box, the submodules are not instanced. Can also drive the outputs
  to 0 if desired.
  """
  ports = []
  disp_str = create_copyright_header()

  for fn in fn_list:
    f = open(fn)

    if(fn.split(".")[-1].startswith("vhd")):
      (mod_name, p) = get_vhdl_port_list(f.read())
    else:
      (mod_name, p) = get_verilog_port_list(f.read())

    # Add to the pin list (if not there already)
    for port in p:
      if(port in ports):
        pass
      else:
        ports.append(port)

    f.close()

  disp_str = disp_str + "module {}(\n".format(mod_name)

  for port in ports:
    print port
    if(port['size'] == ''):
      port['size'] = 1
    if(port['size'] != 1):
      disp_str = disp_str + "\t{0:16}{1:12} {2:12},\n".format(port['type'], "["+str(port['size']-1)+":0]", port['name'])
    else:
      disp_str = disp_str + "\t{0:28} {1},\n".format(port['type'], port['name'])

  disp_str = disp_str[:-2] + "\n\t);\n"

  # If we're creating a black box, don't instance anything inside
  if(bb == False):
    for fn in fn_list:
      disp_str = disp_str + instance_module(fn)
  
  if(drive_0):
    disp_str = disp_str + "\n\n\t// Drive outputs to 0\n\n"
    for port in ports:
      if(port['type'] == 'output'):
        try:
          size = range_to_num_bits(port['size'])
        except:
          print port
        disp_str = disp_str + '\tassign {0:40} = {1}\'h0;\n'.format(port['name'], str(size))

  disp_str = disp_str + "\n\nendmodule\n\n"

  for port in ports:
    if(range_to_num_bits(port['size']) == None):
      disp_str = disp_str +  "// WARNING: port size is unresolved :  {} for port {}\n".format(port['size'], port['name'])
  
  return disp_str

if __name__ == "__main__":  

  commandLine = argparse.ArgumentParser(description='Create a verilog wrapper/blackbox from a list of source verilog/VHDL file(s)',
                                   usage='%(prog)s <module_name> verilog/VHDL file(s)')
  commandLine.add_argument('-mn', '--module_name', default=None)
  commandLine.add_argument('-bb', '--blackbox', action='store_true', default=False)
  commandLine.add_argument('-dz', '--drive_zero', action='store_true', default=False)
  commandLine.add_argument('file_names', help='Source file(s) to instance (verilog or VHDL)', nargs='*')

  opt = commandLine.parse_args()

  if(opt.module_name == None):
    mn = opt.file_names[0].split('.')[0]          # If no module name is supplied, will use the name from the first file.  
  else:
    mn = opt.module_name

  print make_wrapper(mn, opt.file_names, opt.blackbox, opt.drive_zero)

