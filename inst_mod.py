#!/home/prya/usr/bin/python

import argparse


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


def instance_module_style1(module_name, inst_name, ports):
    """
    Connect in the same order as declared in the module
    :param module_name:
    :param ports:
    :return:
    """
    # Instance the module
    disp_str = "\n{} {} (\n".format(module_name, inst_name)

    first_pin = True
    for port in ports:
        if not first_pin:
            disp_str = disp_str + "),\n"
        first_pin = False

        disp_str = disp_str + "    .{0:42}({0}".format(port.name)
    disp_str = disp_str + ")\n  );\n"
    return disp_str


def instance_module_style2(modulename, inst_name, ports):
    """
    Connect with inputs/outputs grouped together
    :param modulename:
    :param inst_name:
    :param ports:
    :return:
    """
    # Instance the module
    if inst_name is None:
        inst_name = "i1_" + modulename

    disp_str = "  {} {} (\n".format(modulename, inst_name)

    first_pin = True
    disp_str = disp_str + "    // Inputs\n"
    for port in ports:
        if port.direction  is "input":
            if first_pin is False:
                disp_str = disp_str + "),\n"
            first_pin = False

            disp_str = disp_str + "    .{0:42}({0}".format(port.name)

    disp_str = disp_str + "),\n\n    // Outputs\n"

    first_pin = True
    for port in ports:
        if port.direction is "output":
            if first_pin is False:
                disp_str = disp_str + "),\n"
            first_pin = False
            disp_str = disp_str + "    .{0:42}({0}".format(port.name)

    disp_str = disp_str + ")\n  );\n"
    return disp_str


def instance_module_style3(module_name, ports):
    raise NotImplementedError("Not much of a use case for this...")


def instance_module_style5(module_name, ports):
    """
    Instance VHDL module
    :param module_name:
    :param ports:
    :return:
    """
    # Instance the module
    disp_str = "\n{0} : {0} port map (\n".format(module_name)

    for port in ports:
        disp_str = disp_str + "    {0:42} => {0},".format(port.name) + '\n'
    disp_str = disp_str[:-1] + "\n  );\n"

    return disp_str


###############################################################################
# Just instance the default way.
def instance_module(module, inst_name=None, style="default"):
    if inst_name is None:
        inst_name = "i1_" + module.module_name

    inst_style_types = {
        "default" : instance_module_style1,
        "group_ports" : instance_module_style2,
        "alphabetical" : instance_module_style3,
        "vhdl" : instance_module_style5
    }
    return inst_style_types[style](module.module_name, inst_name, module.port_list)


if __name__ == "__main__":
    from rtl.port import *
    from rtl.module import *

    test_module = Module()
    test_module.add_port_list(apb_port_list)
    test_module.module_name = "myblk"
    print instance_module(test_module, None, "group_ports")
    asdf

    commandLine = argparse.ArgumentParser(description='Instance modules from a source verilog/VHDL file',
                                          usage='%(prog)s [option|@optFile]... verilog/VHDL file')
    commandLine.add_argument('-g', '--group', help='The IOs are grouped as inputs and outputs', action='store_true',
                             default=False)
    commandLine.add_argument('-d', '--declare', help='Declare the wires needed for hookup', action='store_true',
                             default=False)
    commandLine.add_argument('-v', '--vhdl', help='Instance as VHDL', action='store_true', default=False)
    commandLine.add_argument('file_name', help='Source file to instance (verilog or VHDL)')

    opt = commandLine.parse_args()

    f = open(opt.file_name)

    if ((opt.file_name.split(".")[-1] == "vhd") |
            (opt.file_name.split(".")[-1] == "vhdl")):
        (mn, p) = get_vhdl_port_list(f.read())
    else:
        (mn, p) = get_verilog_port_list(f.read())

    if opt.declare:
        print declare_signals(mn, p)

    if opt.group:
        print instance_module_style2(mn, p)
    elif (opt.vhdl):
        print instance_module_style5(mn, p)
    else:
        print instance_module_style1(mn, p)
