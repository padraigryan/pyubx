#!/usr/bin/env python
import re
import verilog_util as utils

keyword_port = ['input', 'output', 'inout']
keyword_type = ['reg', 'wire', 'logic', 'bit']

keyword_logic = ['always', 'assign', 'always_ff', 'always_comb']

def parse_port_list(portlist_str):
  port_list = []
  port = {}
  port['size'] = 1

  # Remove unneeded code.
  portlist_str = re.sub("task.*endtask",          "", portlist_str, flags=re.DOTALL|re.MULTILINE)
  portlist_str = re.sub("function.*endfunction",  "", portlist_str, flags=re.DOTALL|re.MULTILINE)
  portlist_str = re.sub("\[\s*",  "[", portlist_str, flags=re.DOTALL|re.MULTILINE)
  portlist_str = re.sub("\s*:\s*",  ":", portlist_str, flags=re.DOTALL|re.MULTILINE)
  portlist_str = re.sub("\s*\]",  "]", portlist_str, flags=re.DOTALL|re.MULTILINE)

  for token in filter(None, re.split('[,\t\n ]+', portlist_str)):
    token = token.strip()
    if(token in keyword_port):
      port = {}
      port['size'] = 1
      port['type'] = token
    elif((token == "") or (port == None)):
      pass
    elif(token[0] == '['):                                                      # This is a size description
      port['size'] = utils.range_to_num_bits(token)                             # TODO Handle spaces
    elif(token in keyword_type):
      pass
    elif(token in keyword_logic):                                               # We're into the logic description, doneski!
      return port_list;
    elif(token==';'):                                                           # Last character is a ';'
      port = None
    else:
      if(token[-1] == ';'):
        port['name'] = token[:-1]
        port_list.append(port)
        port = None
      else:
        try:
          port_list.append({'name':token, 'size':port['size'], 'type':port['type']})
        except:
          print "Error:",
          print port 
          print token 

  return port_list

def get_verilog_port_list(verilog_file):

  """
  Get the port list and the rest of the module
  There's two types of ports, verilog-95 and 2001. The old way listed the ports and then the
  the directions.  The new way has all port information together in the port list.  u-blox 
  mostly uses verilog-95!  This function searches for both and then parses using a common
  generic function. 
  """

  verilog_file = utils.strip_comments(verilog_file)
  # Parses the most basic structure of a verilog file.
  m = re.findall(".*module[\W+](.+?)\((.*?)\);(.*)endmodule", verilog_file, re.DOTALL |re.MULTILINE)

  (module_name, pl, arch) = m[0]

  if(pl.find("input ")>=0 or pl.find("output ")>=0 or pl.find("inout ")>=0):
    ports = parse_port_list(pl)         # verilog-2001 format
  else:
    ports = parse_port_list(arch)       # verilog-95 format

  return (module_name, ports)

if __name__=="__main__":

  fn = open("samples/rtl/br_lte_rfic_top.v")
  (mn, prt_lst) = get_verilog_port_list(fn.read())

  for p in prt_lst:
    print p
