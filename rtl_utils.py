import rtl.utils as utils
import argparse
import sys

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

    if opt.compare:
        utils.compare_modules(opt.file_list)
        sys.exit()

    for hdl_file in opt.file_list:

        if opt.instance_tree:
            utils.disp_instance_tree(hdl_file)
            sys.exit()

        if opt.split_netlist:
            utils.split_netlist_files(hdl_file)
            sys.exit()

        if opt.strip_comments:
            utils.disp_strip_comments(hdl_file)
            sys.exit()

        if opt.vhdl_package:
            utils.gen_vhdl_package(hdl_file)

        try:
            if opt.unloaded_inputs | opt.undriven_outputs:
                utils.dangling_pins(opt.unloaded_inputs, opt.undriven_outputs)

            if opt.connections:
                print utils.list_inst_connections(hdl_file, opt.module_type, opt.module_inst)
            if opt.inputs | opt.outputs | opt.inputoutputs:
                utils.disp_io(hdl_file, opt.inputs, opt.outputs, opt.inputoutputs)
            if opt.instances:
                utils.disp_instances(hdl_file)
        except:
            print "Can't open file:" + hdl_file

