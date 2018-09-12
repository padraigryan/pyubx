#!/apps/python/2.7.3/bin/python

import argparse
import sys
import re

"""
Parses a Genus RTL Compiler output log to filter content.
TODO:
- Write gui to allow selective viewing based on
  + The short code
  + Type: Error, Warning, Info's
  + 
- Create a waiver file  
"""

msg_types = ['Error', 'Warning', 'Info', 'Misc']

type_cnt = {}
code_cnt = {}

def display_options(options):
  print "INFO: Running with the following options:"
  for opt in options:
    print "INFO: {:20} - {}".format(opt, options[opt]);

def store_msg(msg, msg_list):
  if msg == None:
    return
  msg_list.append(msg)
  type_cnt[msg['type']] = type_cnt[msg['type']] + 1
  if code_cnt.has_key(msg['code']):
    code_cnt[msg['code']] = code_cnt[msg['code']] + 1
  else:
    code_cnt[msg['code']] = 1

def start_msg(type, short, code, line):
  msg = {}
  if type not in msg_types:
    msg['type']  = 'Misc'
    msg['desc']  = short
    msg['code']  = ""
    msg['short'] = ""
  else:
    msg['type']   =  type
    msg['short']  =  short.replace('-','')
    msg['code']   =  code
    msg['desc']   = " "
  msg['line']   = line
  return msg

def parse_synth_logfile(file_path):
  fh        = open(file_path)
  msg       = None
  linenum   = 1
  msg_list  = []
  
  type_cnt['Error']     = 0
  type_cnt['Warning']   = 0
  type_cnt['Info']      = 0
  type_cnt['Misc']      = 0

  for line in fh.readlines():
    m1 = re.match("(.*)\s+:(.*)\[(.*)\]", line)
    m2 = re.match("\s+: (.*)", line)
    if m1 != None:
      store_msg(msg, msg_list)
      msg = start_msg(  m1.group(1).strip(),        #type
                        m1.group(2).strip(),        #short
                        m1.group(3).strip(),        #code
                        linenum )
    elif m2 != None and msg != None:
      msg['desc'] = msg['desc'] + m2.group(1)
    else:
      store_msg(msg, msg_list)
      msg = start_msg("Misc", "", "", linenum)
      msg['desc'] = line
     
    linenum = linenum + 1
  fh.close()
  return msg_list

def display_msg_counts():
  print "-------------- Number of each Messages Type -----------------------------"
  for t in type_cnt:
    print "{:12} : {}".format(t, type_cnt[t])
  print "\n-------------- Number of each Message Code  ----------------------------"
  for c in code_cnt:
    if c != "":
      print "{:12} : {}".format(c, code_cnt[c])

def write_msg_table(msgs, verbosity):
  import tabulate
  table = []

  for msg in msgs:
    print_msg = True
    if opt.code != None:
      if msg['code'] in opt.code:     ## Match a specific code, example LBR-525
        print_msg = False
      if msg['code'].split('-')[0] in opt.code:    ## Match a code group, example LBR
        print_msg = False
    if opt.type != None:
      if msg['type'] in opt.type:
        print_msg = False
    
    if print_msg:
      if verbosity:
        table.append([ msg['line'], msg['type'], msg['code'], msg['desc']])
      else:
        table.append([ msg['line'], msg['type'], msg['code'], msg['short']])

  print tabulate.tabulate(table, headers=['Line', 'Type', 'Code', 'Description'], tablefmt="psql")

if __name__ == "__main__":  

  print "Genus Log File Parser. u-blox Cork, Ireland (c) 2017"
  print "\nWARNING: This tool is not suitable for signoff.\n\n"

  commandLine = argparse.ArgumentParser(description='Parses Genus log files\n\rU-Blox Cork, Ireland. \nCopyright 2017', usage='%(prog)s log_file')
  commandLine.add_argument('-code',    help='Hide messages with the given code, for example LBR-40 or just LBR for all LBR messages', action='append')
  commandLine.add_argument('-type',    help='Hide messages of the given type', choices = msg_types, action='append')
  commandLine.add_argument('-stats',   help='Display counts of message', action='store_true')
  commandLine.add_argument('-verbose', help='Display the full message as well (best piped to a file)', action='store_true')
  commandLine.add_argument('logfile',  help='The log file to parse', action='store')

  opt = commandLine.parse_args()

  msg_list = parse_synth_logfile(opt.logfile)

  if(opt.stats):
    display_msg_counts()

  write_msg_table(msg_list, opt.verbose)
  
