import xml.etree.ElementTree as ET

def parsexml(xmlfn, mm_data):
  # Parse the ipact register description and remove namespace prefix
  xml = open(xmlfn).read()
  xml = xml.replace("spirit:", "")
  root = ET.fromstring(xml)
  

  dev_name = 'verification_top'
  for ab in root.findall('./memoryMaps/memoryMap/addressBlock'):
    blk_name = ab.find('name').text.replace(dev_name + '_', "")
    rl = []
    for reg in ab.findall('register'):
      reg_name = reg.find('name').text.replace(dev_name + '_' + blk_name + '_', "")
      fl = []
      for field in reg.findall('field'):
        field_name = field.find('name').text.replace(dev_name + '_' + blk_name + '_'  + reg_name + '_', "")
        fl.append((field_name, []))
        #print blk_name, reg_name, field_name
      rl.append((reg_name, fl))
    mm_data.append((blk_name, rl))

