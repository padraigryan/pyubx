#!/apps/python/2.7.3/bin/python

import argparse
import verilog_util as utils

if __name__ == "__main__":  

  commandLine = argparse.ArgumentParser(description='Converts between different ascii binary formats',
                                   usage='%(prog)s  -srcfmt <fmt> -destfmt <fmt> <file>')
  commandLine.add_argument('-srcfmt', choices=['hex', 'rcf', 'bin'], action='store')
  commandLine.add_argument('-destfmt', choices=['hex', 'rcf', 'bin'],  action='store')
  commandLine.add_argument('file_name', help='Source file')

  opt = commandLine.parse_args()

  for line in open(opt.file_name, "r").readlines():
    if opt.srcfmt == 'hex':
      if opt.destfmt == 'bin':
        print utils.to_bin_str('0x' + line, 32)
      else:
        print "Can't convert from hex to " + opt.destfmt
    elif opt.srcfmt == 'bin':                                        # bin - hex
      if opt.destfmt == 'hex':
        print utils.to_hex_str('0b' + line, 32)
      else:
        print "Can't convert from bin to " + opt.destfmt
    elif opt.srcfmt == 'rcf':                                       # rcf - hex
      if opt.destfmt == 'hex':
        print utils.to_hex_str('0b' + line, 32)
      else:
        print "Can't convert from bin to " + opt.destfmt

    else: 
      print "Error: Source format not supported: " + opt.srcfmt
