from RAL_base import *
import client

class RAL_field(RAL_base):
  def __init__(self,label):
    RAL_base.__init__(self, label)
    self.size       = 0
    self.reg_offset = 0
    self.value      = 0

  def _get_field_value(self, val):
    mask = ~(0xFFFFFFFF << self.size)
    return (val>>self.offset) & mask

  def __call__(self, *args, **kwargs):
    if(len(args) == 1):
      print "[INFO] Field Write " + str(hex(args[0])) + " to " + str(hex(self.offset))
      #reg_val = client.reg_read(self.reg_offset)
      print "TODO"

    else:
      print "[INFO] Field Read from " + str(hex(self.reg_offset))
      reg_val = client.reg_read( self.reg_offset )
      field_val = self._get_field_value( reg_val )
      print "[INFO] {0} {1}".format(reg_val, field_val) 

  #def __str__(self):
  #  return "Name:" + self.label+ " Size:" + str(self.size) + " Offset:" + str(self.offset)
