import env
from utils import *
import unittest


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

    # Create Module
    def testParseModule(self):
        dut = Module()

    def testCreateModule(self):
        """

        :return:
        """
        pass
if __name__ == "__main__":
    unittest.main()
