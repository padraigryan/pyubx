import sys
from tabulate import *

from RAL_base import *
from RAL_register import *
from RAL_field import *

# TODO: Should place register_process script with this script.
# TODO: Don't have references to personal areas!!

sys.path.append("/hosted/projects/prya/pyublx/")
from register_process import *

class RAL_subblock(RAL_base):
  """
  Container class for registers:  
  Parse the register map definition spreadsheet to
  get register information. Creates register (and
  implicitly field) instances.
  """
  
  def __init__(self, subblk_offset, f_name, s_name, label):
    global allRegisters

    del allRegisters[:]
    RAL_base.__init__(self, label)

    parse_spreadsheets([f_name], [s_name])
    self.offset          = subblk_offset
    self.last_offset     = subblk_offset

    for reg in allRegisters:
      ral_reg = RAL_register(reg.rawName)
      ral_reg.offset = self.offset + reg.addr
      ral_reg.value  = reg.resetVal

      for field in reg.fields:
        ral_field = RAL_field(field.rawName)
        ral_field.offset      = field.rightBit
        ral_field.size        = field.sizeSpec['bits']
        ral_field.reg_offset  = ral_reg.offset
        ral_reg.add_item(ral_field)

      self.add_item(ral_reg)
      self.last_offset = self.last_offset + 4;

  def __str__(self):
    headers = ["Block", "Register", "Address", "Field", "Position"]
    table = []
    for (reg_name, reg) in self.ral_item.iteritems():
      for (field_name, field) in reg.ral_item.iteritems():
        table.append( [self.label, reg_name, hex(reg.offset), field_name, field.offset] )          
    return tabulate(table, headers, tablefmt="psql")

class RAL_block(RAL_base):
  """
  Top level block for sub-blocks: Doesn't contain any registers, just sub-blocks.  For example
  rx1 is a block while rxrf is sub-block within rx1.
  """
  def __init__(self, subblks, label, offset):
    RAL_base.__init__(self, label)
    for blk in subblks:
      self.add_item(blk)

  def __str__(self):
    headers = ["Block", "Subblock", "Register", "Address", "Field", "Position"]
    table = []
    for (blk_name, blk) in self.ral_item.iteritems():
      for(subblk_name, sub_blk) in blk.ral_item.iteritems():
        for (reg_name, reg) in blk.ral_item.iteritems():
          for (field_name, field) in reg.ral_item.iteritems():
            table.append( [self.label, blk_name, reg_name, hex(reg.offset), field_name, field.offset] )          
    return tabulate(table, headers, tablefmt="psql")

