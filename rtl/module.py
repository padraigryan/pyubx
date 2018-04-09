import sys
import os

sys.path.append("../ubx_flow_regcomp")
import pyverilog_parser
import verilog_util

class Port():
  def __init__(self, name, direction = 'output', comment  = "", size = 1, default=None):
    self.name       = name
    self.size       = size
    self.direction  = direction
    self.default    = default
    self.connection = self.name
    self.comment    = comment
    self.customise  = None

  def __str__(self):
    return "Port: {:30}{:30}{:8}{}".format(self.name, self.connection, self.direction, self.size)

# TODO: Leave this here????
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

# TODO: Leave this here????
def remove_port_from_list(port_name, port_list):
  for p in port_list:
    if (p['name'] == port_name):
      port_list.remove(p)
      return

  raise NameError("Tried to remove a port from list that isn't in the list: " + port_name)


class Module():
  def __init__(self, name=None):
    
    self.port_list    = [] 
    self.sub_blocks   = []
    self.custom_RTL   = ""
    self.wire_list    = []  # Also a list of ports, but that require a wire.

    # If the name is a file, read the details from the RTL instead
    if name == None:
      self.name = ""
    else:
      self.parse_rtl_file(name)
  
  def add_port(self, port_name, direction, comment ="", size = 1, def_val = None):
    """
    loads a port dictionary with information related to that port.
    :param port_name:
    :param direction:
    :param comment:
    :param size:
    :param def_val:
    :return:
    """

    if find_port(port_name, self.port_list):
      #print "WARN: Tried to repeatedly add port " + port_name
      return
  
    self.port_list.append(Port(port_name, direction, comment, size, def_val))
    return self.port_list[-1]

  def remove_port(self,  port_name):
    for port in self.port_list:
      if port.name == port_name:
        #print "INFO: {} Removing port : {}".format(self.name ,port_name)
        self.port_list.remove(port)
        return True
    print "INFO: Failed to remove port : " + port_name
    return False

  def get_port(self, port_name):
    for port in self.port_list:
      if port.name == port_name:
        return port
    return None

  def has_port(self,  port_name):
    for port in self.port_list:
      if port.name == port_name:
        return True
    return False
    
  def change_connection(self, cur_port, new_connect):
    for p in self.port_list:
      if p.name == cur_port:
        p.connection = new_connect
        return  # break out

  def add_wire(self, wire):
    for w in self.wire_list:
      if (w.name == wire.name)  or (w.name[:-2] == wire.name[:-2]):
        #print "WARN: Already have wire declared for " + w.name
        return
    if self.has_port(wire.name):
      return

    #print "DEBUG: Adding wire " + wire.name
    self.wire_list.append(wire)

  def add_custom_RTL(self, rtl_str):
    self.custom_RTL = self.custom_RTL + "\t" + rtl_str + "\n"

  
  def instance_module(self, instance_name=None):

    if instance_name == None:
      instance_name = self.module_name

    inst_str = "\n{} {} (\n".format(self.module_name, instance_name)

    for port in self.port_list:
      inst_str = inst_str + "    .{0:42}({1}),\n".format(port.name, port.connection)

    # Remove the last comma and close instance
    inst_str = "{}\n ); // {} {}\n".format(inst_str[:-2], self.module_name, instance_name)
    return inst_str

  # Place holder to add custom methods after the object is created
  def customise(self, dummy=None):
    pass

  def export_rtl(self, file_name = None, black_box = False):
    rtl_str = verilog_util.create_copyright_header()

    if self.module_name == None:
      raise NameError("This module still doesn't have a name")

    if file_name == None:
      file_name = self.module_name + ".v"

    print "INFO: Writing out RTL to file: " + file_name
    rtl_str = rtl_str + "module " + self.module_name + "(\n"

    rtl_str = rtl_str + self._write_pin_list()
    rtl_str = rtl_str + self._write_port_list()
  
    if not black_box:
      rtl_str = rtl_str + "  // Internal interconnect wiring\n"
      
      for wire in self.wire_list:
        if wire.size > 1:
          rtl_str = rtl_str + "  {:13} [{:2}:0]      {};\n".format("wire", wire.size-1, wire.connection)
        else:
          rtl_str = rtl_str + "  {:13}             {};\n".format("wire", wire.connection)

      rtl_str = rtl_str + "\n\n" + self.custom_RTL  + "\n\n"

      rtl_str = rtl_str + "  // Sub-module Instance\n"
      for blk in self.sub_blocks:
        rtl_str = rtl_str + blk.instance_module()


    rtl_str = rtl_str + "endmodule\n"

    # Write out the RTL (to file or as a string)
    if file_name == None:
      return rtl_str
    else:
      if not os.access(file_name, os.W_OK):
        print "\n\nWARN: " + file_name + " is not checked out, do you want to check it out (y/n) : ",
        choice = raw_input()
        if choice in ['', 'y', 'Y']:
          os.system('icmp4 edit ' + file_name)
        else:
          print "WARN : {} was not written".format(file_name)
          return
      fh = open(file_name, "w")
      print >>fh, rtl_str
      fh.close()

  def parse_rtl_file(self, file_name):
    """
    Parse a verilog file to create a new Module object with all the ports filled out.
    """
    (mn, ports)       = pyverilog_parser.get_verilog_port_list(open(file_name).read())
    self.module_name  = mn

    for port in ports:
      self.add_port(port['name'], port['type'], "", verilog_util.range_to_num_bits(port['size']) )

  def _write_pin_list(self):
    disp_str = ""
    for port in self.port_list:
      disp_str = disp_str + '  {},\n'.format(port.name)

    disp_str = disp_str[:-2]  # remove the last comma

    disp_str = disp_str +  '  );\n\n'
    return disp_str

  def _write_port_list(self):
    disp_str = ""
    for port in self.port_list:
      range_str = ""

      # Set options
      if port.size >  1:
        range_str = "[{:2}: 0]".format(port.size-1)

      # Write IO port line
      disp_str = disp_str + "{:8}{:8}{:12}{:60}// {}\n".format( port.direction, \
                                                                "wire" if port.direction == 'output' else '   ', \
                                                                range_str, 
                                                                port.name +';', \
                                                                port.comment )
    disp_str = disp_str +  '\n\n'
    return disp_str

  def __str__(self):
    return "Module: {} - {} ports, {} sub-instances".format(self.module_name, \
                                                            len(self.port_list), \
                                                            len(self.sub_blocks)
                                                           )
  def __iter__(self):
    return iter(self.port_list)


if __name__ == "__main__":  
  top_mod = Module()
  low_mod = Module()

  top_mod.parse_rtl_file("samples/rtl/sample.v")
  low_mod.parse_rtl_file("samples/rtl/sample2.v")
  top_mod.sub_blocks.append(low_mod);

  # Create the wires
  for port in top_mod:
    if(port.direction == "inout"):
        print "wire        {}_PAD;".format(port.name)

  # Create the reg
  for port in top_mod:
    if(port.direction == "inout"):
      print "reg        {}_reg;".format(port.name)
    else:
      if(port.size > 1):
        print "reg [{}:0] {};".format(port.size-1, port.name)
      else:
        print "reg        {};".format(port.name)


  top_mod.export_rtl("my_sample.v")
