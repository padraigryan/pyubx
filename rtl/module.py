#!/usr/bin/env python
import hdl_parser
import utils
from port import *


class Module:
    def __init__(self, name=None):

        self.port_list = []
        self.sub_blocks = []
        self.custom_RTL = ""
        self.wire_list = []  # Also a list of ports, but that require a wire.
        self.module_name = ""
        self.inst_name = None

        # If the name is a file, read the details from the RTL instead
        if name is None:
            self.name = ""
        else:
            self.parse_rtl_file(name)

    def add_port_list(self, pl):
        for p in pl:
            self.add_port(p.name, p.direction, p.comment, p.size)

    def add_port(self, port_name, direction, comment="", size=1, def_val=None):
        """
        loads a port dictionary with information related to that port.
        :param port_name:
        :param direction:
        :param comment:
        :param size:
        :param def_val:
        :return:
        """

        if find_port(port_name, self.port_list):
            # print "WARN: Tried to repeatedly add port " + port_name
            return

        self.port_list.append(Port(port_name, direction, comment, size, def_val))
        return self.port_list[-1]

    def remove_port(self, port_name):
        """

        :param port_name:
        :return:
        """
        for p in self.port_list:
            if p.name == port_name:
                # print "INFO: {} Removing port : {}".format(self.name ,port_name)
                self.port_list.remove(p)
                return True
        print "INFO: Failed to remove port : " + port_name
        return False

    def get_port(self, port_name):
        """

        :param port_name:
        :return:
        """

        for p in self.port_list:
            if p.name == port_name:
                return p
        return None

    def has_port(self, port_name):
        """

        :param port_name:
        :return:
        """
        for p in self.port_list:
            if p.name == port_name:
                return True
        return False

    def has_input(self, port_name):
        """

        :param port_name:
        :return:
        """
        for p in self.port_list:
            if p.name == port_name and p.direction == "input":
                return True
        return False

    def has_output(self, port_name):
        """

        :param port_name:
        :return:
        """
        for p in self.port_list:
            if p.name == port_name and p.direction == "output":
                return True
        return False

    def change_connection(self, cur_port, new_connect):
        """

        :param cur_port:
        :param new_connect:
        :return:
        """
        for p in self.port_list:
            if p.name == cur_port:
                p.connection = new_connect
                return  # break out

    def add_wire(self, wire):
        """

        :param wire:
        :return:
        """
        for w in self.wire_list:
            if w.name is wire.name:
                # print "WARN: Already have wire declared for " + w.name
                return
        if self.has_port(wire.name):
            return

        # print "DEBUG: Adding wire " + wire.name
        self.wire_list.append(wire)

    def add_custom_RTL(self, rtl_str):
        """

        :param rtl_str:
        :return:
        """
        self.custom_RTL = self.custom_RTL + "  " + rtl_str + "\n"

    def instance_module(self, instance_name=None):
        """

        :param instance_name:
        :return:
        """

        if instance_name is None:
            if self.inst_name is None:
                instance_name = self.module_name
            else:
                instance_name = self.inst_name

        inst_str = "\n{} {} (\n".format(self.module_name, instance_name)

        for p in self.port_list:
            inst_str = inst_str + "    .{0:42}({1}),\n".format(p.name, p.connection)

        # Remove the last comma and close instance
        inst_str = "{}\n ); // {} {}\n".format(inst_str[:-2], self.module_name, instance_name)
        return inst_str

    # Place holder to add custom methods after the object is created
    def customise(self, dummy=None):
        pass

    def add_subblock(self, new_subblk):
        """

        :param new_subblk:
        :return:
        """
        cnt = 0;
        for sb in self.sub_blocks:
            if new_subblk.module_name == sb.module_name:
                cnt = cnt + 1
        new_subblk.inst_name  = "i{}_{}".format(cnt, new_subblk.module_name)
        self.sub_blocks.append(new_subblk)

    def export_rtl(self, file_name=None, black_box=False):
        """

        :param file_name:
        :param black_box:
        :return:
        """
        rtl_str = utils.create_copyright_header()

        if self.module_name is None:
            raise NameError("This module still doesn't have a name")

        rtl_str = rtl_str + "module " + self.module_name + "(\n"

        rtl_str = rtl_str + self._write_pin_list()
        rtl_str = rtl_str + self._write_port_list()

        if not black_box:
            rtl_str = rtl_str + "  // Internal interconnect wiring\n"

            for wire in self.wire_list:
                if wire.size > 1:
                    rtl_str = rtl_str + "  {:13} [{:2}:0]      {};\n".format("wire", wire.size - 1, wire.connection)
                else:
                    rtl_str = rtl_str + "  {:13}             {};\n".format("wire", wire.connection)

            rtl_str = rtl_str + "\n\n" + self.custom_RTL + "\n\n"

            if len(self.sub_blocks) > 0:
                rtl_str = rtl_str + "  // Sub-module Instance\n"

            for blk in self.sub_blocks:
                if blk.inst_name is None:
                    blk.inst_name = "i{}_{} ".format(blk, blk.module_name)
                rtl_str = rtl_str + blk.instance_module(blk.inst_name)

        rtl_str = rtl_str + "endmodule\n"

        # Write out the RTL (to file or as a string)
        if file_name is None:
            return rtl_str
        else:
            fh = open(file_name, "w")
            print >> fh, rtl_str
            fh.close()

    def parse_rtl_file(self, file_name):
        """
        Parse a verilog file to create a new Module object with all the ports filled out.

        :param file_name:
        :return:
        """
        try:
            port_list = hdl_parser.get_hdl_ports(file_name)
        except ValueError:
            port_list = hdl_parser.get_hdl_ports(file_name, file_name.split('/')[-1].split('.')[-2])

        self.add_port_list(port_list)
        self.module_name = hdl_parser.get_block_name(file_name)

    def _write_pin_list(self):
        disp_str = ""
        for p in self.port_list:
            disp_str = disp_str + '  {},\n'.format(p.name)

        disp_str = disp_str[:-2]  # remove the last comma

        disp_str = disp_str + '  );\n\n'
        return disp_str

    def _write_port_list(self):
        disp_str = ""
        for p in self.port_list:
            range_str = ""

            # Set options
            if p.size > 1:
                range_str = "[{:2}: 0]".format(p.size - 1)

            # Write IO port line
            disp_str = disp_str + "{:8}{:8}{:12}{:60}// {}\n".format(p.direction,
                                                                     "wire" if p.direction == 'output' else '   ',
                                                                     range_str,
                                                                     p.name + ';',
                                                                     p.comment)
        disp_str = disp_str + '\n\n'
        return disp_str

    def __str__(self):
        return "Module: {} - {} ports, {} sub-instances".format(self.module_name,
                                                                len(self.port_list),
                                                                len(self.sub_blocks)
                                                                )

    def __iter__(self):
        return iter(self.port_list)


if __name__ == "__main__":

    top_mod = Module()
    low_mod = Module()
    custom_mod = Module()

    top_mod.parse_rtl_file("../test/samples/rtl/sample.v")
    low_mod.parse_rtl_file("../test/samples/rtl/sample2.v")
    top_mod.sub_blocks.append(low_mod)
    custom_mod.add_port_list(apb_port_list)
    custom_mod.module_name = "myblk"
    top_mod.sub_blocks.append(custom_mod)

    top_mod.export_rtl("/tmp/my_sample.v")
