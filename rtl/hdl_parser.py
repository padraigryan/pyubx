#!/usr/bin/env python
import re
import utils
import port as hdl_port

_keyword_port = ['input', 'output', 'inout']
_keyword_type = ['reg', 'wire', 'logic', 'bit']
_keyword_logic = ['always', 'assign', 'always_ff', 'always_comb', 'parameter']


def get_vhdl_port_list(vhdl_file):
    # Clean up to make processing easier
    vhdl_file = utils.strip_comments(vhdl_file)
    vhdl_file = vhdl_file.replace('\n', ' ')
    vhdl_file = vhdl_file.replace('\t', ' ')
    vhdl_file = vhdl_file.lower()

    # Get the generic's default
    generics = re.findall("generic\W*\((.+?)\);", vhdl_file)
    ports = re.findall("port\W*\((.+?)\)\W+end.*;", vhdl_file)
    ports = ports[0]

    # Process the Generics
    for generic_line in generics[0].split(';'):
        generic_result = re.search("(.*)\W*:\W*(.*)\w*:=\W*(.)", generic_line)
        generic_name = generic_result.group(1).strip()
        generic_value = generic_result.group(3)
        ports = ports.replace(generic_name, generic_value)

    # Process the Ports
    module_port_list = []
    for port_line in ports.split(';'):
        port = hdl_port.Port("Unknown")
        ports_details = re.split(', |: |\W+', port_line)
        port.size = utils.range_to_num_bits(ports_details[-1])
        port.direction = ports_details[-2]
        for port_name in ports_details[:-2]:
            port.name = port_name
            module_port_list.append(port)
            port = hdl_port.Port("Unknown")

    return module_port_list


def get_block_name(hdl_fname):
    """
    TODO: Add support for VHDL and verilog and don't repeat this code in the get_verilog_port function
    :param hdl_fname:
    :return:
    """
    with open(hdl_fname, "r") as fh:
        verilog_file = fh.read()
        fh.close()

    verilog_file = utils.strip_comments(verilog_file)
    verilog_file = verilog_file.replace('\n', ' ')
    verilog_file = verilog_file.replace('\t', ' ')
    # Parses the most basic structure of a verilog file.
    m = re.findall("module[\W+](.+?)\((.*?)\);(.*?)endmodule", verilog_file, re.MULTILINE)
    return m[0][0]


def get_verilog_port_list(verilog_file, target_module=None):
    """
    Get the port list and the rest of the module
    There's two types of ports, verilog-95 and 2001. The old way listed the ports and then the
    the directions.  The new way has all port information together in the port list.  u-blox
    mostly uses verilog-95!  This function searches for both and then parses using a common
    generic function.
    """

    verilog_file = utils.strip_comments(verilog_file)
    verilog_file = verilog_file.replace('\n', ' ')
    verilog_file = verilog_file.replace('\t', ' ')

    # Parses the most basic structure of a verilog file.
    m = re.findall("module[\W+](.+?)\((.*?)\);(.*?)endmodule", verilog_file, re.MULTILINE)

    if len(m) > 1 and target_module is None:
        found_mods = []
        for (module_name, pl, arch) in m:
            found_mods.append(module_name)
        raise ValueError("Found more than one module: " + " ".join(found_mods))

    for (module_name, pl, arch) in m:
        if module_name == target_module or target_module is None:
            if pl.find("input ") >= 0 or pl.find("output ") >= 0 or pl.find("inout ") >= 0:
                mod_ports = _parse_verilog_port_list(pl)  # verilog-2001 format
            else:
                mod_ports = _parse_verilog_port_list(arch)  # verilog-95 format
            return mod_ports


def _parse_verilog_port_list(portlist_str):
    port_list = []
    port = hdl_port.Port("unknown")

    # Remove unneeded code.
    portlist_str = re.sub("task.*endtask", "", portlist_str, flags=re.DOTALL | re.MULTILINE)
    portlist_str = re.sub("function.*endfunction", "", portlist_str, flags=re.DOTALL | re.MULTILINE)
    portlist_str = re.sub("\[\s*", "[", portlist_str, flags=re.DOTALL | re.MULTILINE)
    portlist_str = re.sub("\s*:\s*", ":", portlist_str, flags=re.DOTALL | re.MULTILINE)
    portlist_str = re.sub("\s*\]", "]", portlist_str, flags=re.DOTALL | re.MULTILINE)

    for token in filter(None, re.split('[,\t\n ]+', portlist_str)):
        token = token.strip()
        if token in _keyword_port:
            port = hdl_port.Port("unknown")
            port.size = 1
            port.direction = token
        elif (token == "") or (port is None):
            pass
        elif token[0] == '[':  # This is a size description
            port.size = utils.range_to_num_bits(token)
        elif token in _keyword_type:
            pass
        elif token in _keyword_logic:  # We're into the logic description, doneski!
            return port_list
        elif token == ';':  # Last character is a ';'
            port = None
        else:
            if token[-1] == ';':
                port.name = token[:-1]
                port_list.append(port)
                port = None
            else:
                try:
                    port.name = token
                    port_list.append(port)
                    port = hdl_port.Port("unknown", port.direction, port.comment, port.size, port.default)
                except KeyError:
                    print "Error:",
                    print port
                    print token

    return port_list


def get_hdl_ports(hdl_fname, target_module=None):
    """

    :param hdl_fname:
    :param target_module:
    :return:
    """
    with open(hdl_fname, "r") as fh:
        hdl_str = fh.read()
        fh.close()

    if hdl_fname.endswith(".vhd") or hdl_fname.endswith(".vhdl"):
        return get_vhdl_port_list(hdl_str)
    else:
        return get_verilog_port_list(hdl_str, target_module)


if __name__ == "__main__":
    modules = get_hdl_ports("../test/samples/rtl/sample2.v", "sample2")
    modules = get_hdl_ports("../test/samples/rtl/sample.v")
    #modules = get_hdl_ports("../test/samples/rtl/ram.vhdl")
    ports = modules
    for p in ports:
        print str(p)
