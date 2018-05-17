#!/usr/bin/env python

import argparse
import sys

import rtl.utils as verilog_util
import vcd_utils

psel_name = ""
pwdata_name = ""
prdata_name = ""
pwrite_name = ""
paddr_name = ""
penable_name = ""


def get_apb_sig_name(signals, apb_name):
    for sig in signals:
        if apb_name in sig.lower():
            return sig
    raise ValueError("Could not find '{}' signal in VCD variables".format(apb_name))


def apb_decode(apb_signals, timestamp):
    # TODO: IS this needed here?
    sys.path.append("/hosted/projects2/prya/pyublx")
    import verilog_util

    psel = apb_signals[psel_name]['value']
    pwdata = apb_signals[pwdata_name]['value']
    prdata = apb_signals[prdata_name]['value']
    pwrite = apb_signals[pwrite_name]['value']
    paddr = apb_signals[paddr_name]['value']
    penable = apb_signals[penable_name]['value']

    if penable == '1' and psel == '1':
        if pwrite == '1':
            print "{} : Write 0x{} to   0x{}".format(timestamp, verilog_util.to_hex_str(pwdata),
                                                     verilog_util.to_hex_str('0' + paddr))
        else:
            print "{} : Read  0x{} from 0x{}".format(timestamp, verilog_util.to_hex_str(prdata),
                                                     verilog_util.to_hex_str('0' + paddr))


if __name__ == "__main__":
    commandLine = argparse.ArgumentParser(description='Single step firmware/simulation tool for AMS VCD generation',
                                          usage='%(prog)s [options] <test case name>')
    commandLine.add_argument('vcd_file_name', help='Source VCD file to edit', action='store')

    opt = commandLine.parse_args()

    vcd = vcd_utils.vcd_file(opt.vcd_file_name)
    vcd.timeunit = 'us'
    print vcd

    psel_name = get_apb_sig_name(vcd.signals, 'psel')
    pwdata_name = get_apb_sig_name(vcd.signals, 'pwdata')
    prdata_name = get_apb_sig_name(vcd.signals, 'prdata')
    pwrite_name = get_apb_sig_name(vcd.signals, 'pwrite')
    paddr_name = get_apb_sig_name(vcd.signals, 'paddr')
    penable_name = get_apb_sig_name(vcd.signals, 'penable')

    vcd.parse_vcd_vars(apb_decode, [penable_name])
