#!/usr/bin/env python

import rtl.utils as utils
import argparse
import sys

if __name__ == "__main__":

    commandLine = argparse.ArgumentParser(description='Parse a list of verilog files and displays information',
                                          usage='%(prog)s {options} verilog file(s)')
    commandLine.add_argument('-in', '--inputs', action='store_true', help='List of inputs', default=False)
    commandLine.add_argument('-out', '--outputs', action='store_true', help='List of outputs', default=False)
    commandLine.add_argument('-inout', '--inputoutputs', action='store_true', help='List of bidir ports', default=False)
    commandLine.add_argument('-li', '--list_instances', action='store_true', help='List of instances', default=False)
    commandLine.add_argument('-lit', '--list_instance_tree', action='store_true',
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
    commandLine.add_argument('-mw', '--module_wrapper', action='store_true',
                             help="Wraps the supplied modules in a top level module", default=False)
    commandLine.add_argument('-ms', '--module_stub', action='store_true',
                             help="Creates an empty wrapper or blackbox around a module", default=False)
    commandLine.add_argument('-dz', '--drivezero', action='store_true',
                             help="Drive stub output to 0, only valid with --module_stub, otherwise outputs float",
                             default=False)
    commandLine.add_argument('-inst', '--instance',  action='store_true', default=False,
                             help='Dumps a instance of the given module.')
    commandLine.add_argument('-d', '--declare',  action='store_true', default=False,
                             help='Declare the wires needed for hookup. Only valid with the -inst parameter')
    commandLine.add_argument('-v', '--vhdl', help='Instance as VHDL', action='store_true', default=False)

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

    if opt.module_wrapper:
        print utils.module_wrapper(opt.file_list)

    if opt.module_stub:
        if len(opt.file_list) != 1:
            raise ValueError("Can only crate a stub for a single file at a time")
        print utils.create_stub(opt.file_list[0], opt.drivezero)

    for hdl_file in opt.file_list:

        if opt.instance:
            print utils.instance_module(hdl_file)

        if opt.list_instance_tree:
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
            if opt.list_instances:
                utils.disp_instances(hdl_file)
        except:
            print "Can't open file:" + hdl_file

