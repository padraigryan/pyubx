#!/home/prya/usr/bin/python

import datetime
from string import Template
import os
from inst_mod import *  # This is to be phased out
import pyverilog_parser

base_spec = {
            'h': 16,
            'x': 16,
            'd': 10,
            's': 10,
            'b': 2
            }


def create_copyright_header(comment_char='//'):
    """
    Returns a string with the ICM tags and a creation date embedded.
    """

    disp_str = '-----------------------------------------------------------------------------\n\
Company    : u-blox Cork, Ireland\n\
Created    : ${DATE}\n\
Last commit: $$Date:$$\n\
Updated by : $$Author:$$\n\
----------------------------------------------------------------------------\n\
Copyright (c) ${YEAR} u-blox Cork, Ireland\n\
----------------------------------------------------------------------------\n\
$$Id:$$\n\
AUTO-GENERATED: Do Not Hand Edit\n\
-----------------------------------------------------------------------------\n\n'
    comment_char = comment_char + ' '
    disp_str = comment_char + disp_str.replace("\n", '\n' + comment_char) + '\n\n'

    t = Template(disp_str)

    return t.substitute(DATE=datetime.datetime.now().strftime("%A, %d %B %Y %I:%M%p"),
                        YEAR=datetime.datetime.now().strftime("%Y"))


def range_to_num_bits(range_str):
    """
    Handles the following only.
    1) Extract the width from the bus name, e.g. bus_name[2:0]
    2) Handle [] and <> brackets
    3) Big and little endianess (including non-zero to non-zero ranges, eg bus_name[6:5])
    4) Single bits wires
    """
    range_str = str(range_str)

    if range_str == '':
        return 1

    bus_range = re.split('\[|\<', range_str)  # Get the bus_range section at the end of the bus name
    if len(bus_range) > 1:
        bus_range = bus_range[1]
    else:
        return 1  # It's a bare signal name without brackets (eg sig_name)

    bus_range = bus_range[:-1]  # Remove the closing bracket

    if len(bus_range.split(':')) == 1:  # There's brackets but no bus_range, single bit (eg bus_name[6])
        return 1

    try:
        left = int(bus_range.split(':')[0])  # Get the left bound (exception if not a number)
        right = int(bus_range.split(':')[1])  # Get the right bound (exception if not a number)
        if left >= right:
            return left - right + 1
        else:
            return right - left + 1
    except:
        return None


def _detect_base(in_str):
    """
    Verilog:
    8'hA5
    -3'sd5        -- unsupported at the moment
    'b010101

    C:
    0xAF
    0b1010


    Returns tuplet of base (int), trimmed string, size (int)
    """

    # If it's a signed number.
    if in_str.find('s') >= 0 or in_str.find('-') >= 0:
        raise NotImplementedError("Doesn't currently support signed values; TBD")

    if in_str.find("'") >= 0:  # Verilog format
        num_parts = in_str.lower().split("'")

        in_str = num_parts[1][1:]
        base = base_spec[num_parts[1][0]]

        # If the size isn't spec'ed, then use min number of bit to contain this number.
        if num_parts[0] != '':
            size = int(num_parts[0])
        else:
            size = int(in_str, base).bit_length()

    elif in_str[:2] in ["0x", "0d", "0b"]:  # C format
        base = base_spec[in_str[1]]
        in_str = in_str[2:]
        size = int(in_str, base).bit_length()
    else:  # Raw number - assumed decimal
        base = 10
        size = int(in_str, base).bit_length()

    return base, in_str, size


def to_bin_str(num, bit_str_len=None):
    """
    Converts <in_str> from it's source base which is automatically detected if not supplied in <in_base>.
    Throws an exception if it can't determine the base.  Returns a binary string WITHOUT any base specification.
    Returns: string
    """
    if type(num) is int:
        num = str(num)

    (base, in_str, size) = _detect_base(num)
    if bit_str_len is not None:
        size = bit_str_len
    else:
        size = 32

    return str(bin(int(in_str, base))[2:].zfill(size))


def to_hex_str(num, hex_str_len=32):
    """
  Converts <in_str> from it's source base which is automatically detected if not supplied in <in_base>.  
  Throws an exception if it can't determine the base.  Returns a hex string WITHOUT any base specification.
  Returns: string
  """

    if type(num) is int:
        num = str(num)

    (base, in_str, size) = _detect_base(num)
    if hex_str_len is not None:
        size = hex_str_len

    return str(hex(int(in_str, base))[2:].zfill(size / 4)).upper()


def to_dec_str(num):
    """
    Converts <in_str> from it's source base which is automatically detected if not supplied in <in_base>.
    Throws an exception if it can't determine the base.  Returns a dec string WITHOUT any base specification.
    Returns: string
    """
    if type(num) is int:
        num = str(num)

    (base, in_str, size) = _detect_base(num)

    return str(int(in_str, base))


def join_hdl_paths(path_bits, hw_separator='.'):
    """
    like the name says, defaults to a period but can pass it any symbol.
    path_bits is a list of the layers of hierarchy in order.
    """
    full_path = ""
    try:
        for path_bit in path_bits:
            if (full_path == ""):
                full_path = path_bit
            else:
                full_path = full_path + hw_separator + path_bit
    except:
        print "Couldn't join:"
        print path_bits
        raise

    return full_path


def _search_keyword(s_str, keyword):
    s_str = re.sub(r'\W+', '', s_str)
    if s_str.find(keyword) < 0:
        return False
    else:
        return True


def strip_comments(src_code):
    # Remove compound comments
    src_code = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", src_code)
    # Remove oneline comments
    src_code = re.sub(re.compile("//.*?\n"), "\n", src_code)
    return src_code


def disp_strip_comments(file_name):
    """
    TODO: Handle VHDL files
    """
    print strip_comments(open(file_name).read())


def list_instances(verilog_file_name):
    """
    Parses the verilog file and returns a list of tuples containing:
    1) The instance type
    2) The instance name
    Limitations:
    Mostly intended for structural verilog, some RTL will cause problems.

    TODO: 1) Instances with parameter definitions
          2) Instances within a generate statement
    """
    try:
        f = open(verilog_file_name)
        verilog = f.read()
        f.close()
    except:
        return []

    inst_list = []
    block_cnt = 0
    line_cnt = 0
    statement = ''

    verilog = strip_comments(verilog)
    for line in verilog.split('\n'):
        line_cnt = line_cnt + 1

        # Remove comments
        sline = line.strip().split()

        if _search_keyword(line, 'begin'):
            block_cnt = block_cnt + 1
        if (_search_keyword(line, 'end') is True) & (_search_keyword(line, 'endcase') is False):
            block_cnt = block_cnt - 1

        if block_cnt >= 1:
            pass
        elif statement != '':  #
            if line.find(';') > 0:
                pass
            else:
                statement = statement + line
                statement = ''                      #  TODO: Wasted statement

        elif len(sline) >= 2:
            # Find the module name
            if sline[0] == "module":
                module_name = sline[1].strip('(')
            elif (sline[0] in ['always', 'initial', 'logic', 'wire', 'reg', 'input', 'output', 'inout', 'assign',
                               'integer']):
                pass

            elif (line.find('.') > 0) | (line.find(')') > 0) | (line.find(',') > 0):
                # connect_list.append(''.join(c for c in a if c not  in ['.' , '(' , ')', ',']).split())        # Removes the .(), and returns the port connection.
                #  print sline[0]
                pass
            else:
                inst_list.append((sline[0], sline[1].strip('()')))

    if module_name is None:
        print "Error: couldn't find module name in file"
        sys.exit()

    return inst_list


def list_inst_connections(verilog_file_name, mod_type, inst_name):
    """
    Parses the file name to find the instance of the given module type.  Builds a
    list of connection tuples in that instance.
    Note: Assumes .name(wire), format. .* or positional connections will not work.
    """
    f = open(verilog_file_name)
    verilog = f.read()
    f.close()

    block_cnt = 0
    line_cnt = 0
    found_inst = False
    connect_list = []

    for line in verilog.split('\n'):
        line_cnt = line_cnt + 1

        # Remove comments
        line = line.split("//")[0]
        sline = line.strip().split()

        if _search_keyword(line, 'begin'):
            block_cnt = block_cnt + 1
        if (_search_keyword(line, 'end') is True) & (_search_keyword(line, 'endcase') is False):
            block_cnt = block_cnt - 1

        if line.find(');') >= 0:
            found_inst = False

        if block_cnt >= 1:
            pass
        elif len(sline) >= 2:

            if sline[0] in ['always', 'initial', 'logic', 'wire', 'reg', 'input', 'output', 'inout']:
                pass
            elif (sline[0] == mod_type) & (sline[1].strip('()') == inst_name):
                found_inst = True
            elif (found_inst is True) & (line.find('.') >= 0) & (line.find(')') > 0):
                connect_list.append(tuple(''.join(c for c in line if c not in ['.', '(', ')',
                                                                               ',']).split()))  # Removes the .(), and returns the port connection.

    return connect_list


def disp_instances(verilog_file_name):
    inst_list = list_instances(verilog_file_name)
    print "{:30} {}".format('Module Name', 'Instance Name')
    for (t, i) in inst_list:
        print "{:30} {}".format(t, i)
    print " "


def disp_instance_tree(verilog_file_name, level=0):
    """ Recursively reads in verilog files and builds a tree of hierarchy.
      Makes the following assumptions:
      - module name and file name are the same
      - verilog files end with .v or .sv
      - all files are in the current directory TODO: fix this
      Do a glob of the RTL directory and search the list for suitable file
    """
    inst_list = list_instances(verilog_file_name)
    for (m_name, i_name) in inst_list:
        print "{0}{1} ({2})".format(level * "   ", i_name, m_name)
        dirpath = os.path.dirname(verilog_file_name)
        if dirpath == "":
            dirpath = '.'
        disp_instance_tree(dirpath + '/' + m_name + '.v', level + 1)


def disp_io(fn, inputs, outputs, inout):
    (mn, ports) = pyverilog_parser.get_verilog_port_list(open(fn).read())

    if inputs:
        print "Module:" + mn + " Inputs"
    for port in ports:
        if (port['type'] == 'input') & (inputs):
            print "{}".format(port['name'])
    print " "

    if outputs:
        print "Module:" + mn + " Outputs"
    for port in ports:
        if (port['type'] == 'output') & (outputs):
            print "{}".format(port['name'])
    print " "

    if inout:
        print "Module:" + mn + " Inout"
    for port in ports:
        if ((port['type'] == 'inout') & (inout)):
            print "{}".format(port['name'])
    print " "


def split_netlist_files(netlist_file_name):
    # Create the netlist directory if not already there
    if not os.path.exists('./netlist'):
        os.makedirs('./netlist')

    # Open the source netlist
    fh = open(netlist_file_name, 'r')
    fout = None

    for line in fh:
        if line.find('module ') == 0:
            fname = line.split()[1].split('(')[0]
            print "Module: " + fname
            try:
                fout = open('netlist/' + fname + '.v', 'w')
            except:
                fout = open('netlist/' + fname[:250] + '~.v', 'w')
                print "Shortened file name: " + 'netlist/' + fname[:250] + '~.v'

        if line.find('endmodule') == 0:
            fout.write(line)
            fout.close()

        if fout is not  None:
            if fout.closed is False:
                fout.write(line)


def compare_modules(modules):
    import tabulate
    if len(modules) != 2:
        print "ERROR: Can only compare 2 files"
        return

    (mn1, p1) = pyverilog_parser.get_verilog_port_list(open(modules[0]).read())
    (mn2, p2) = pyverilog_parser.get_verilog_port_list(open(modules[1]).read())

    modules[0] = os.path.abspath(modules[0])
    modules[1] = os.path.abspath(modules[1])

    comprefix = len(os.path.commonprefix(modules))
    print comprefix

    modules[0] = '~' + modules[0][comprefix:]
    modules[1] = '~' + modules[1][comprefix:]
    for p in p1:
        p['width'] = range_to_num_bits(p['size'])

    for p in p2:
        p['width'] = range_to_num_bits(p['size'])

    table = []
    for p in p1:
        if p in p2:
            table.append([p['name'], p['width'], p['width'], p['type']])
            p2.remove(p)
        else:
            table.append([p['name'], p['width'], ' ', p['type']])

    for p in p2:
        table.append([p['name'], ' ', p['width'], p['type']])

    print tabulate.tabulate(table, headers=['name', modules[0], modules[1], "Direction"], tablefmt="psql")


def gen_vhdl_package(filename):
    filename = os.path.abspath(filename)

    (mn, port_list) = pyverilog_parser.get_verilog_port_list(open(filename).read())

    mn = mn.strip()

    vhdl_port_list = ""
    for port in port_list:
        if port['size'] == 1:
            size = 'std_logic'
        else:
            size = 'std_logic_vector(' + str(port['size'] - 1) + ' downto 0)'
        dir = port['type'].replace('put', '')

        # vhdl_port_list = "\t\t\t{40:}\: {} {}".format(vhdl_port_list, dir, size)
        vhdl_port_list = vhdl_port_list + "\t\t\t{:40}: {:5} {};\n".format(port["name"], dir, size)

    vhdl_port_list = vhdl_port_list[:-2]

    print create_copyright_header('--')
    print """
library ieee;
use     ieee.std_logic_1164.all;
use     ieee.numeric_std.all;

package pkg_{0}_comp is

  component {0}  is
    port (
    {1}
  );
  end component {0};

end package pkg_{0}_comp;

""".format(mn, vhdl_port_list)


def dangling_pins(dangling_in, dangling_out):
    print "TODO:// Write this function!"
    print "ERROR: Nothing done"
    raise NotImplementedError


def unused_declarations(dangling_in, dangling_out):
    print "TODO:// Write this function!"
    print "ERROR: Nothing done"
    raise NotImplementedError


def list_flops(verilog):
    """
  NotImplementedError
  Searches for always blocks with a pos/negedge clock. Returns the following info:
  - The clock
  - The reset
  - The flops
  -- size
  -- reset value
  -- dependencies??? 
  """
    print "TODO:// Write this function!"
    print "ERROR: Nothing done"
    raise NotImplementedError


def lint_code(verilog):
    """
  NotImplementedError
  Searches for the following:
  - Dangling pins
  - Unused variables
  - bad variable names
  -- TBD what this means?
  - Warning: mixed blocking/non-blocking statements.
  """
    print "TODO:// Write this function!"
    print "ERROR: Nothing done"
    raise NotImplementedError


if __name__ == "__main__":

    commandLine = argparse.ArgumentParser(description='Parse a list of verilog files and displays information',
                                          usage='%(prog)s xls file(s)')
    commandLine.add_argument('-in', '--inputs', action='store_true', help='List of inputs', default=False)
    commandLine.add_argument('-out', '--outputs', action='store_true', help='List of outputs', default=False)
    commandLine.add_argument('-inout', '--inputoutputs', action='store_true', help='List of bidir ports', default=False)
    commandLine.add_argument('-inst', '--instances', action='store_true', help='List of instances', default=False)
    commandLine.add_argument('-inst_tree', '--instance_tree', action='store_true',
                             help='List of instances in a hierarchical tree format', default=False)
    commandLine.add_argument('-con', '--connections', action='store_true', help='List of connections for an instance',
                             default=False)
    commandLine.add_argument('-com', '--compare', action='store_true', help='Compare the ports of 2 modules',
                             default=False)
    commandLine.add_argument('-unld_in', '--unloaded_inputs', action='store_true',
                             help='List the inputs that are unloaded internally', default=False)
    commandLine.add_argument('-undrv_out', '--undriven_outputs', action='store_true',
                             help='List the outputs that are undriven internally', default=False)
    commandLine.add_argument('-vhdl_pkg', '--vhdl_package', action='store_true',
                             help='Dumps out a VHDL package for a verilog module', default=False)
    commandLine.add_argument('-mt', '--module_type')
    commandLine.add_argument('-mi', '--module_inst')
    commandLine.add_argument('-sc', '--strip_comments', action='store_true',
                             help='Strips all the comments from the source files', default=False)
    commandLine.add_argument('-sn', '--split_netlist', action='store_true', default=False,
                             help='Split a single file netlist into a set of files in a new directory called netlist')
    commandLine.add_argument('file_list', help='List of verilog files', nargs='*')
    opt = commandLine.parse_args()

    if (opt.compare):
        compare_modules(opt.file_list)
        sys.exit()

    for file in opt.file_list:

        if opt.instance_tree:
            disp_instance_tree(file)
            sys.exit()

        if opt.split_netlist:
            split_netlist_files(file)
            sys.exit()

        if opt.strip_comments:
            disp_strip_comments(file)
            sys.exit()

        if opt.vhdl_package:
            gen_vhdl_package(file)

        try:
            if opt.unloaded_inputs | opt.undriven_outputs:
                dangling_pins(opt.unloaded_inputs, opt.undriven_outputs)

            if opt.connections:
                print list_inst_connections(file, opt.module_type, opt.module_inst)
            if opt.inputs | opt.outputs | opt.inputoutputs:
                disp_io(file, opt.inputs, opt.outputs, opt.inputoutputs)
            if opt.instances:
                disp_instances(file)
        except:
            print "Can't open file:" + file

    """
  assert to_bin_str(5, 4)  == "4'b0101"
  assert to_bin_str(5)     == "32'b00000000000000000000000000000101"
  assert to_hex_str(10, 4) == "4'hA"
  assert to_hex_str(10, 16)== "16'h000A"
  assert to_hex_str(10)    == "32'h0000000A"

  assert range_to_num_bits('sig_name') == 1
  assert range_to_num_bits('bus_name[5:0]') == 6
  assert range_to_num_bits('bus_name[11:5]') == 7
  assert range_to_num_bits('bus_name[5:11]') == 7
  assert range_to_num_bits('bus_name[5]') == 1

  assert range_to_num_bits('bus_name<5:0>') == 6
  assert range_to_num_bits('bus_name<11:5>') == 7
  assert range_to_num_bits('bus_name<5:11>') == 7
  assert range_to_num_bits('bus_name<5>') == 1
  """
