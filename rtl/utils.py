import datetime
from string import Template
import sys
import os
import re
import hdl_parser as parser
from module import Module
import logging
import port as rtl_port

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
    4) Single bits wire
    5) vhdl std_logic and std_logic_vector
    """

    range_str = str(range_str).lower()

    if range_str == '':
        return 1

    if range_str.startswith("std_logic "):
        return 1

    if range_str.startswith("std_logic_vector"):
        bus_range = re.search("std_logic_vector\W*\((.*)\W+downto\W+(.*)\)", range_str)
        high = eval(bus_range.group(1))
        low = eval(bus_range.group(2))
        return high - low + 1

    bus_range = re.split('\[|\<', range_str)  # Get the bus_range section at the end of the bus name
    if len(bus_range) > 1:
        bus_range = bus_range[1]
    else:
        return 1  # It's a bare signal name without brackets (eg sig_name)

    bus_range = bus_range[:-1]  # Remove the closing bracket

    if len(bus_range.split(':')) == 1:  # There's brackets but no bus_range, single bit (eg bus_name[6])
        return 1

    try:
        left = eval(bus_range.split(':')[0])  # Get the left bound (exception if not a number)
        right = eval(bus_range.split(':')[1])  # Get the right bound (exception if not a number)
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
    TODO: can this be done with a ".".join call?
    """
    full_path = ""
    for path_bit in path_bits:
        if full_path == "":
            full_path = path_bit
        else:
            full_path = full_path + hw_separator + path_bit

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

    TODO: 0) Just Use pyparsing
    TODO: 1) Instances with parameter definitions
    TODO: 2) Instances within a generate statement
    """
    with open(verilog_file_name) as verilog_file_h:
        verilog = verilog_file_h.read()
        verilog_file_h.close()

    verilog = verilog.replace("\n", "")
    m = re.findall("(.+?)\s+(.+?)\s*\(.*\);", verilog)

    # print m.group(1)
    print
    print m[0]
    asdf

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
                statement = ''  # TODO: Wasted statement

        elif len(sline) >= 2:
            # Find the module name
            if sline[0] == "module":
                module_name = sline[1].strip('(')
            elif (sline[0] in ['always', 'initial', 'logic', 'wire', 'reg', 'input', 'output', 'inout', 'assign',
                               'integer', 'parameter', 'task', 'function']):
                pass

            elif (line.find('.') > 0) | (line.find(')') > 0) | (line.find(',') > 0):
                # connect_list.append(''.join(c for c in a if c not  in ['.' , '(' , ')', ',']).split())
                #  Removes the .(), and returns the port connection.
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
    (mn, ports) = parser.get_verilog_port_list(open(fn).read())

    if inputs:
        print "Module:" + mn + " Inputs"

    for port in ports:
        if port.direction == 'input' and inputs:
            print "{}".format(port.name)
    print " "

    if outputs:
        print "Module:" + mn + " Outputs"
    for port in ports:
        if port.direction == 'output' and outputs:
            print "{}".format(port.name)
    print " "

    if inout:
        print "Module:" + mn + " Inout"
    for port in ports:
        if port.direction == 'inout' and inout:
            print "{}".format(port.name)
    print " "


def split_netlist_files(netlist_file_name):
    """
    Super useful function for syntheised netlists! Will create a directory called "netlist" and create individual
    files for each module in the single netlist file.
    :param netlist_file_name: The source netlist file to split up
    :return: None
    """
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

        if fout is not None:
            if fout.closed is False:
                fout.write(line)


def compare_modules(modules):
    """
    Compares 2 modules and lists the ports that are common and the port that are different by name, size or direction.
    :param modules: List of 2 rtl files to compare.
    :return:
    """
    if len(modules) != 2:
        print "ERROR: Can only compare 2 files"
        return

    mod1 = Module(modules[0])
    mod2 = Module(modules[1])

    modules[0] = os.path.abspath(modules[0])
    modules[1] = os.path.abspath(modules[1])

    print "File 1: " + modules[0]
    print "File 2: " + modules[1]

    comprefix = len(os.path.commonprefix(modules))

    modules[0] = '~' + modules[0][comprefix:]
    modules[1] = '~' + modules[1][comprefix:]

    table = []
    for port1 in mod1.port_list:
        if mod2.has_port(port1.name):
            port2 = mod2.get_port(port1.name)
            if port2.direction != port1.direction:
                table.append([port1.name, port1.size, port2.size, port1.direction + "/" + port2.direction])
            else:
                table.append([port1.name, port1.size, port2.size, port1.direction])
        else:
            table.append([port1.name, port1.size, ' ', port1.direction])

    for port2 in mod2.port_list:
        if not mod1.has_port(port2.name):
            table.append([port2.name, ' ', port2.size, port2.direction])

    print "+{}+{}+{}+{}+".format(40 * "-", 20 * "-", 20 * "-", 10 * "-")
    print "|{:40}|{:20}|{:20}|{:10}|".format("Port", mod1.module_name, mod2.module_name, "Direction")
    print "+{}+{}+{}+{}+".format(40 * "-", 20 * "-", 20 * "-", 10 * "-")
    for row in table:
        print "|{:40}|{:10}          |{:10}          |{:10}|".format(row[0], row[1], row[2], row[3])
    print "+{}+{}+{}+{}+".format(40 * "-", 20 * "-", 20 * "-", 10 * "-")


def create_stub(file_name, drivezero=False):
    """
    :param file_name: The module file to create the wrapper for
    :param drivezero: Should the outputs be driven to zero.
    :return: An empty stub module
    """
    stub = Module(file_name)

    for port in stub:
        if port.direction == "output" and drivezero is True:
            stub.add_custom_RTL("assign {} = {}'b{};".format(port.name, port.size, "0" * port.size))

    return stub.export_rtl()


def input_to_all_blks(port_name, blklist, prefix=None, suffix=None):
    def _input_to_all_blks(port_name, blklist, prefix=None, suffix=None):
        cnt = 0
        for blk in blklist:
            for port in blk.port_list:
                try:
                    dest_port_name = port.name[:-len((filter(lambda x: port.name.endswith(x), suffix))[0])]
                except:
                    dest_port_name = port.name
                try:
                    src_port_name = port_name[:-len((filter(lambda x: port_name.endswith(x), suffix))[0])]
                except:
                    src_port_name = port_name

                if dest_port_name == src_port_name and port.direction == "input":
                    cnt = cnt + 1
                    break
                try:
                    dest_port_name = port.name[:-len((filter(lambda x: port.name.startswith(x), prefix))[0])]
                except:
                    dest_port_name = port.name
                try:
                    src_port_name = port_name[:-len((filter(lambda x: port_name.startswith(x), prefix))[0])]
                except:
                    src_port_name = port_name

                if dest_port_name == src_port_name and port.direction == "input":
                    cnt = cnt + 1
                    break
        return cnt

    cnt = _input_to_all_blks(port_name, blklist, None, None)
    if cnt != 0:
        return cnt

    # There's no match, strip the suffix and try again
    cnt = _input_to_all_blks(port_name, blklist, None, suffix)
    if cnt != 0:
        return cnt

    # Still no match, try stripping the prefix
    cnt = _input_to_all_blks(port_name, blklist, prefix, None)
    return cnt


def output_from_all_blks(port_name, blklist, prefix=None, suffix=None):
    def _output_from_all_blks(port_name, blklist, prefix=None, suffix=None):
        cnt = 0
        for blk in blklist:
            for port in blk.port_list:
                # Remove the Suffix and test
                try:
                    dest_port_name = port.name[:-len((filter(lambda x: port.name.endswith(x), suffix))[0])]
                except:
                    dest_port_name = port.name
                try:
                    src_port_name = port_name[:-len((filter(lambda x: port_name.endswith(x), suffix))[0])]
                except:
                    src_port_name = port_name

                if dest_port_name == src_port_name and port.direction == "output":
                    cnt = cnt + 1
                    break

                # Remove the Prefxi and test
                try:
                    dest_port_name = port.name[:-len((filter(lambda x: port.name.startswith(x), prefix))[0])]
                except:
                    dest_port_name = port.name
                try:
                    src_port_name = port_name[:-len((filter(lambda x: port_name.startswith(x), prefix))[0])]
                except:
                    src_port_name = port_name

                if dest_port_name == src_port_name and port.direction == "output":
                    cnt = cnt + 1
                    break
        return cnt

    cnt = _output_from_all_blks(port_name, blklist, None, None)
    if cnt != 0:
        return cnt

    # There's no match, strip the suffix and try again
    cnt = _output_from_all_blks(port_name, blklist, None, suffix)
    if cnt != 0:
        return cnt

    # Still no match, try stripping the prefix
    cnt = _output_from_all_blks(port_name, blklist, prefix, None)
    return cnt


def remove_suffix(full_name, suffix):
    try:
        return full_name[:-len((filter(lambda x: full_name.endswith(x), suffix))[0])]
    except TypeError:
        return full_name
    except IndexError:
        return full_name


def remove_prefix(full_name, prefix):
    try:
        return full_name[:-len((filter(lambda x: full_name.startswith(x), prefix))[0])]
    except TypeError:
        return full_name
    except IndexError:
        return full_name


def create_wrapper(file_list, wrapper_name="top_level", prefix=None, suffix=None, blackbox=False):
    """
    Reads each of the rtl modules from file_list.
    Creates a toplevel module with all the ports
    Instance each sub module with the following rules of connecting pins:
        1) if the pin is only an input to each sub module, it's an input from the top
        2a) if the pin is output from more than one module,  prepend inst and bring to top level
        2b) if the pin is output from one module only, bring to top level
        2c) if pin is output from one module and input to another, interconnect only.
        2d) if pin is output from one module only and input to multiple subblocks, interconnect only
        3) Repeat rules 1-3 are repeated with the prefix/suffix removed/added.
        4) Repeat rules 1-4 with fuzzy matching
        5) All other pins are brought to the top level with the same directionality
    Black box modules only bring out pins but don't instance sub modules
    Suffix/Prefix lists help to better match pins.
    TODO: Pass a top level black box and hook subblocks into it.
    TODO: Pass a translation function for known port name changes.

    :param file_list: A list of tuples that contain HDL files to instance in the wrapper and instance names.
    Give the same filename multiple times for multiple instances,
    :param wrapper_name:  The name to give the top level wrapper module
    :param prefix: A list  of known prefixes to help with port matching
    :param suffix: A list of known suffixes to help with port matching
    :param blackbox: Only instance the toplevel module without the sub-blocks.
    :return: A new module with the sub-modules instanced and wired according to the rules above.
    """

    log = logging.getLogger("WRAPPER")
    logging.basicConfig(level=logging.DEBUG)

    # Create the top level module
    if os.path.exists(wrapper_name):
        top_level = Module(wrapper_name)
    else:
        top_level = Module()
        top_level.module_name = os.path.split(wrapper_name)[-1].split('.')[-2]

    # Add all the sub modules
    for (subblock_fn, inst_name) in file_list:
        top_level.add_subblock(Module(subblock_fn))
        top_level.sub_blocks[-1].inst_name = inst_name

    for subblk in top_level.sub_blocks:             # Connect each block
        for blk_port in subblk:                     # Connect each port on the block

            # Now check for internal connections or if we need to add to the toplevel.
            num_outputs = output_from_all_blks(blk_port.name, top_level.sub_blocks, prefix, suffix)
            num_inputs = input_to_all_blks(blk_port.name, top_level.sub_blocks, prefix, suffix)
            if blk_port.direction == "input":
                if num_outputs == 0:
                    top_level.add_port_list([blk_port])
                    if num_inputs > 1:
                        log.warn("Input  : {}:{} - From top - Single input from top to multiple instances".format(
                            subblk.inst_name, blk_port.name))
                    else:
                        log.debug("Input  : {}:{} - From top".format(subblk.inst_name, blk_port.name))
                elif num_outputs == 1:
                    log.debug("Input  : {}:{} - Internal connection".format(subblk.inst_name, blk_port.name))
                    blk_port.connection = remove_prefix(remove_suffix(blk_port.name, suffix), prefix)
                else:
                    log.warn("Input  : {}:{} - Multiple drivers".format(subblk.inst_name, blk_port.name))

            elif blk_port.direction == "output":
                if num_outputs == 1:
                    # Straight point to point internal connection or...
                    # One output connected to multiple inputs for internal blocks else...
                    # Not an internal connection, bring to the top level.
                    if num_inputs > 0:
                        log.debug("Output : {}:{} - Internal Single output to one or more inputs".format(subblk.inst_name,
                                                                                                      blk_port.name))
                        blk_port.connection = remove_prefix(remove_suffix(blk_port.name, suffix), prefix)
                        top_level.add_wire(rtl_port.Port(blk_port.connection, "output", "", blk_port.size))
                    else:
                        log.debug("Output : {}:{} - To top".format(subblk.inst_name, blk_port.name))
                        top_level.add_port_list([blk_port])
                else:
                    # N outputs connected to N inputs:
                    if num_inputs == 0:
                        log.debug(
                            "Output : {}:{} - Multiple To top, prefix instance".format(subblk.inst_name, blk_port.name))
                        blk_port.connection = subblk.inst_name + "_" + blk_port.name
                        toplevelport = rtl_port.Port(blk_port.connection, "output", blk_port.comment, blk_port.size)
                        top_level.add_port_list([toplevelport])
                    elif num_outputs == num_inputs:
                        log.warn("TODO: Multiple outputs connected to N input(s)")
                        blk_port.connection = "/* Unconnected */"
                    else:
                        log.warn("TODO: Multiple outputs connected to one or more input(s) need to be concatenated")
                        blk_port.connection = "/* Unconnected */"
            else:
                log.error("Can only handle input/output type ports")

    return top_level.export_rtl()


def gen_vhdl_package(filename):
    filename = os.path.abspath(filename)

    (mn, port_list) = parser.get_verilog_port_list(open(filename).read())

    mn = mn.strip()

    vhdl_port_list = ""
    for port in port_list:
        if port.size == 1:
            size = 'std_logic'
        else:
            size = 'std_logic_vector(' + str(port.size - 1) + ' downto 0)'
        directory = port.direction.replace('put', '')

        # vhdl_port_list = "\t\t\t{40:}\: {} {}".format(vhdl_port_list, dir, size)
        vhdl_port_list = vhdl_port_list + "\t\t\t{:40}: {:5} {};\n".format(port.name, directory, size)

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


def declare_signals(module_name, ports):
    """
    Declare the signals
    :param module_name:
    :param ports:
    :return:
    """
    disp_str = "\n  // " + module_name + "\n"
    for port in ports:
        disp_str = disp_str + "  wire {0:44}{1};\n".format(port.size, port.name)
    return disp_str


def instance_module_default_style(module_name, inst_name, ports):
    """
    Connect in the same order as declared in the module
    :param module_name:
    :param inst_name:
    :param ports:
    :return:
    """
    # Instance the module
    disp_str = "\n{} {} (\n".format(module_name, inst_name)

    for port in ports:
        disp_str = disp_str + "    .{0:42}({0}),\n".format(port.name)
    disp_str = disp_str[:-2] + "\n);\n"
    return disp_str


def instance_module_group_style(modulename, inst_name, ports):
    """
    Connect with inputs/outputs grouped together
    :param modulename:
    :param inst_name:
    :param ports:
    :return:
    """
    # Instance the module
    disp_str = "  {} {} (\n".format(modulename, inst_name)

    disp_str = disp_str + "    // Inputs\n"
    for port in ports:
        if port.direction == "input":
            disp_str = disp_str + "    .{0:42}({0}),\n".format(port.name)

    disp_str = disp_str + "\n    // Outputs\n"

    for port in ports:
        if port.direction == "output":
            disp_str = disp_str + "    .{0:42}({0}),\n".format(port.name)

    # Remove the last comma
    disp_str = disp_str[:-2] + "\n);\n\n\n"
    return disp_str


def instance_module_alpha_style(module_name, ports):
    raise NotImplementedError("Not much of a use case for this...")


def instance_module_vhdl_style(module_name, entity_name, ports):
    """
    Instance VHDL module
    :param module_name:
    :param entity_name:
    :param ports:
    :return:
    """
    # Instance the module
    disp_str = "\n{} : {} port map (\n".format(entity_name, module_name)

    for port in ports:
        disp_str = disp_str + "    {0:42} => {0},".format(port.name) + '\n'
    disp_str = disp_str[:-1] + "\n  );\n"

    return disp_str


def instance_module(fn, inst_name=None, style="default"):
    """
    Instance the module gving in the RTL file.  If no instance name is given then a default one is provided.

    :param fn: RTL file containing module to instance
    :param inst_name: optional instance name, default will be generated
    :param style: optional style, options are default or group
    :return: string of the instance
    """
    mod_to_inst = Module(fn)

    if inst_name is None:
        inst_name = "i1_" + mod_to_inst.module_name

    inst_style_types = {
        "default": instance_module_default_style,
        "group": instance_module_group_style,
        "alphabetical": instance_module_alpha_style,
        "vhdl": instance_module_vhdl_style
    }
    return inst_style_types[style](mod_to_inst.module_name, inst_name, mod_to_inst.port_list)


def _dangling_pins(dangling_in, dangling_out):
    print "TODO:// Write this function!"
    print "ERROR: Nothing done"
    raise NotImplementedError


def _unused_declarations(dangling_in, dangling_out):
    print "TODO:// Write this function!"
    print "ERROR: Nothing done"
    raise NotImplementedError


def _list_flops(verilog):
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


def _lint_code(verilog):
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
    # print list_instances("../test/samples/rtl/sample.v")
    # print instance_module("../test/samples/rtl/sample.v", "i1_sample", "vhdl")
    # compare_modules(["../test/samples/rtl/sample2.v",
    #                 "../test/samples/rtl/sample.v"])
    try:
        os.remove("../test/samples/rtl/toplevel_wrapper.v")
    except:
        pass
    print create_wrapper([("../test/samples/rtl/blkA.v", "rx1"),
                          ("../test/samples/rtl/blkA.v", "rx2"),
                          ("../test/samples/rtl/blkB.v", "i0")],
                         "../test/samples/rtl/toplevel_wrapper.v",
                         None,
                         ["_i", "_o", "xCI"])
