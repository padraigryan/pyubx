from module import *
import unittest


class ModuleTest(unittest.TestCase):
    @staticmethod
    def testSimpleHier(self):
        top_mod = Module()
        low_mod = Module()

        top_mod.parse_rtl_file("test/samples/sample.v")
        low_mod.parse_rtl_file("test/samples/sample2.v")
        top_mod.sub_blocks.append(low_mod)

        top_mod.export_rtl("my_sample.v")
