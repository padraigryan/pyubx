import env
from utils import *
import unittest
from module import Module


class UtilsTest(unittest.TestCase):

    def testVhdlStdLogicRange(self):
        self.assertEqual(range_to_num_bits("std_logic"), 1)

    def testVhdlStdLogicVectorRange(self):
        self.assertEqual(range_to_num_bits("std_logic_vector(3 downto 0)"), 4)

    def testVhdlStdLogicVectorGenericRange(self):
        self.assertEqual(range_to_num_bits("std_logic_vector(6-1 downto 1+1)"), 4)

    def testToBinStrFixedSize(self):
        self.assertEqual(to_bin_str("4'hA", 4), "1010")

    def testToBinStrDefaultSize(self):
        self.assertEqual(to_bin_str(5), "00000000000000000000000000000101")

    def testToHexStrFixedSize(self):
        self.assertEqual(to_hex_str(10, 4), "A")

    def testToHexStrFixedSize16(self):
        self.assertEqual(to_hex_str(10, 16), "000A")

    def testToHexStrDefaultSize(self):
        self.assertEqual(to_hex_str(10), "0000000A")

    def testToDecStrFixedSize(self):
        self.assertEqual(to_dec_str(10), "10")

    def testToDecStrFixedSize16(self):
        self.assertEqual(to_dec_str(10), "10")

    def testToDecStrDefaultSize(self):
        self.assertEqual(to_dec_str(10), "10")

    def testRangeToNumBitsDefault(self):
        self.assertEqual(range_to_num_bits('sig_name'), 1)

    def testRangeToNumBitsBusToZero(self):
        self.assertEqual(range_to_num_bits('bus_name[5:0]'), 6)

    def testRangeToNumBitsBusRangeDown(self):
        self.assertEqual(range_to_num_bits('bus_name[11-1:5-1]'), 7)

    def testRangeToNumBitsBusRangeUp(self):
        self.assertEqual(range_to_num_bits('bus_name[5:11]'), 7)

    def testRangeToNumBitsSingleBit(self):
        self.assertEqual(range_to_num_bits('bus_name[5]'), 1)

    def testRangeToNumBitsAngleBusToZero(self):
        self.assertEqual(range_to_num_bits('bus_name<5:0>'), 6)

    def testRangeToNumBitsAngleBusRangeDown(self):
        self.assertEqual(range_to_num_bits('bus_name<11+1:5+1>'), 7)

    def testRangeToNumBitsAngleBusRangeUp(self):
        self.assertEqual(range_to_num_bits('bus_name<5:11>'), 7)

    def testRangeToNumBitsAngleSingleBit(self):
        self.assertEqual(range_to_num_bits('bus_name<5>'), 1)

    def testJoinPathDefault(self):
        self.assertEqual(join_hdl_paths(["p1", "p2"]), "p1.p2")

    # HDL Path Join
    def testJoinPathUnderscore(self):
        self.assertEqual(join_hdl_paths(["p1", "p2"], '_'), "p1_p2")

    def testJoinPathsEmpty(self):
        self.assertEqual(join_hdl_paths([]), "")

    # Comments

    # RTL Introspection
    def testListInstances(self):
        pass

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

    def testListInstances(self):
        inst_list = [
                    ("signal_sync", "master_ld_pclk_i"),
                    ("reset_sync",  "PResetxRBI_sync_i"),
                    ("clockmux2",   "aux_dfe_clk_mux"),
                    ("clockmux2",   "I_adcClkOut_mux"),
                    ("clockmux2",   "CHI1adcClkMux_mux"),
                    ("clockmux2",   "CHI2adcClkMux_mux")
                    ]

        (exp_mod_type, exp_inst_name) = zip(*inst_list)
        mod = list_instances("../test/samples/rtl/sample.v")
        for (mod_type, inst_name) in mod:
            self.assertTrue(mod_type in exp_mod_type and inst_name in exp_inst_name)

    # Create Module
    def testParseModule(self):
        tc_expected_port_list = ["sig1", "sig2", "sig3", "sig4", "sig5", "PClkxCI", "PResetxARBI", "PEnClkxSO",
                                 "PEnClkxSI", "PAddrxDI", "PSelxSI", "PEnablexSI", "PWritexSI",	"PWDataxDI",
                                 "PReadyxSO", "PRDataxDO", "PSlverrxSO", "bidir_sig"]

        dut = Module("../test/samples/rtl/sample2.v")

        tc_tot_num_bit = 0
        tc_ip_num_bit = 0
        tc_op_num_bit = 0
        tc_bi_num_bit = 0
        for port in dut.port_list:
            self.assertTrue((port.name in tc_expected_port_list), "Didn't find epected port: " + port.name)
            tc_tot_num_bit = tc_tot_num_bit + port.size
            if port.direction == "input":
                tc_ip_num_bit = tc_ip_num_bit + port.size
            elif port.direction == "output":
                tc_op_num_bit = tc_op_num_bit + port.size
            elif port.direction == "inout":
                tc_bi_num_bit = tc_bi_num_bit + port.size

        self.assertEqual(tc_tot_num_bit, 109)
        self.assertEqual(tc_ip_num_bit, 73)
        self.assertEqual(tc_op_num_bit, 35)
        self.assertEqual(tc_bi_num_bit, 1)

    def testCreateModule(self):
        """

        :return:
        """
        pass


if __name__ == "__main__":
    unittest.main()
