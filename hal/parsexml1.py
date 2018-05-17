import xml.etree.ElementTree as ET

def parsexml(xmlfn):
    # Parse the ipact register description and remove namespace prefix
    xml = open(xmlfn).read()
    xml = xml.replace("spirit:", "")
    root = ET.fromstring(xml)

    dev_name = 'verification_top'
    ab = root.findall('./memoryMaps/memoryMap/addressBlock')

    for ab in root.findall('./memoryMaps/memoryMap/addressBlock'):
        blk_name = ab.find('name').text.replace(dev_name + '_', "")
        fh = open(blk_name + ".xml", "w")
        for reg in ab.findall("register"):
          reg.getchildren()
          asdf

        fh.write(ab.text)
        fh.close()
        asdfas

parsexml("/hosted/projects2/prya/icm/prya+ic_Breithorn_Verification+trunk+80/hal/verification_top/outputs/ipxact/verification_top.xml")
