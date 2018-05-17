
from RAL_base import *

class RAL_register(RAL_base):
  def __init__(self, label):
    RAL_base.__init__(self, label)
    self.value = 0

  def getval(self):
    return self.value

  def setval(self,val):
    self.value = val
