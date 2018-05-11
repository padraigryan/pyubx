#!/usr/bin/env python

import env
from module import *
import unittest


class ModuleTest(unittest.TestCase):

    def testSimpleHier(self):
        top_mod = Module()
        low_mod = Module()
        addr_mod = Module()

        top_mod.parse_rtl_file("../test/samples/rtl/sample.v")
        low_mod.parse_rtl_file("../test/samples/rtl/sample2.v")
        # addr_mod.parse_rtl_file("../test/samples/rtl/adder.vhd")
        top_mod.sub_blocks.append(low_mod)
        # top_mod.sub_blocks.append(addr_mod)

        top_mod.export_rtl("my_sample.v")


if __name__ == "__main__":
    unittest.main()