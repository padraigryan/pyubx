import client


class RAL_base:

  def __init__(self, label):
    self.label = label
    self.ral_item = {}      # could be field, register or a block
    self.offset = 0
    self.value = 0
    #self.description = ""

  def add_item(self, new_item):
    self.ral_item[new_item.label] = new_item

  """
  Return a string to represent this object.
  """
  def __str__(self):
    full_str = self.label + ":" + str(hex(self.offset))

    for i in self.ral_item:
      full_str = full_str + ' ' + str(i)

    return full_str

  """
  This is where the action is:  When a parameter is passed, it is the value to be written.
  If there's not parameter, a read is assuemd.  Call the appropriate read/write method from
  here.
  """
  def __call__(self, *args, **kwargs):
    if(len(args) == 1):
      print "[INFO] RAL: Write " + str(hex(args[0])) + " to " + str(hex(self.offset))
      client.reg_write(self.offset, args[0])
      return 0
    else:
      read_val = client.reg_read(self.offset)
      print "[INFO] RAL: Read " + str(hex(read_val)) + " from " + str(hex(self.offset))
      return read_val

  """
  Allows the caller to iterate over all the subfields
  """
  def __iter__(self):
    return iter(self.ral_item)

  """
  dir is used for autocompletion, should return a list of subfields to the caller.  This only
  works in an interpreter.
  """
  def __dir__(self):
    auto_comp = []
    for (key, item) in self.ral_item.iteritems():
      auto_comp.append( key )

    return auto_comp

  """
  Allows the dot notation to access the memory model.
  If valid returns the next lower 'item'
  """
  def __getattr__(self, name):
    if name.startswith('__') and name.endswith('__'):
      #return
      return super(dict, self).__getattribute__(name)

    try:
      return self.ral_item[name]
    except KeyError as err:
      print "[WARN] Couldn't find " + str(err) + ". Options are:"
      for (key, item) in self.ral_item.iteritems():
        print key
    except:
      pass

  """
  Displays the whole register map. This can be very verbose for higher level blocks since
  everything is displayed
  """
  def display(self):
    for (blk_name, blk) in self.ral_item.iteritems():
      print blk

  """
  These are needed because I define the __getattr__ method.  Force pickler to treat it
  like a regular class
  """
  def __getstate__(self):
    return self.__dict__

  def __setstate__(self,d):
    return self.__dict__.update(d)


