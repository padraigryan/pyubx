#!/usr/bin/env python

import argparse
import sys
import re

"""
TODO:
  VCD Import:
    1) Save the whole VCD into data structures
    2) Parse the header data
    3) Handle non-zero time start.
    4) Get the end time

  VCD Export:
    1) A text 

"""
k_timescales = {
    'fs': 1000000000000000.0,
    'ps': 1000000000000.0,
    'ns': 1000000000.0,
    'us': 1000000.0,
    'ms': 1000.0
}


def convert_time_unit(time, to_unit=None):
    unit = time[-2:].lower()
    if unit in k_timescales:
        if to_unit is None:
            return int(time[:-2]) * k_timescales[unit]
        else:
            to_unit = to_unit.lower()
            return str((int(time[:-2]) / k_timescales[unit]) * k_timescales[to_unit]) + to_unit

    else:
        return time


class VCDFile:

    def __init__(self, fn, create_new=False):
        self.signals = {}
        self.symbol = [33]
        self.timeunit = 'ns'
        if create_new:
            self.vcd_file_contents = ""
            self.fh = open(opt.vcd_file_name, 'w')
            self.set_vcd_comment('u-blox vcd editor (c) 2017')
            self.set_vcd_date()
            self.set_vcd_timescale('1fs')

        else:
            self.fh = open(fn, 'r')
            self.vcd_file_contents = self.fh.readlines()
            (self.time, self.scale) = self._get_vcd_timescale()
            self._decode_definition()
            self.fh.close()

    def export_vcd(self):
        print self.fh.write(self.vcd_file_contents)
        self.fh.close()

    def set_vcd_date(self):
        import datetime
        cur_date = datetime.date.today().strftime("%B %d, %Y")
        self.vcd_file_contents = self.vcd_file_contents + "$date\n\t{}\n$end\n\n".format(cur_date)

    def set_vcd_timescale(self, timescale):
        self.vcd_file_contents = self.vcd_file_contents + "$timescale\n\t{}\n$end\n\n".format(timescale)

    def set_vcd_comment(self, comment):
        self.vcd_file_contents = self.vcd_file_contents + "$comment\n\t{}\n$end\n\n".format(comment)

    def set_start_scope(self, new_scope):
        self.vcd_file_contents = self.vcd_file_contents + "$scpoe module {}  $end\n\n".format(new_scope)

    def set_end_scope(self, end_scope):
        self.vcd_file_contents = self.vcd_file_contents + "$upscpoe module {}  $end\n\n".format(end_scope)

    def _get_next_symbol(self):
        """
        Starts with a single ascii symbol (33 = ", skip space) until they are all used, then
        add a second symbol, a 3rd etc.
        """
        for i in range(0, len(self.symbol)):
            if self.symbol[i] >= 126:
                if i == len(self.symbol) - 1:
                    self.symbol.append(33)
                self.symbol[i] = 33
            else:
                self.symbol[i] = self.symbol[i] + 1
                break
        symbol = ""
        for sym in self.symbol:
            symbol = symbol + chr(sym)
        return symbol

    def add_new_var(self, sig_name, sig_type, sig_size="1"):
        signal = {"type": sig_type,
                  "size": sig_size,  # TODO take this from the signal name
                  "symbol": self._get_next_symbol(),
                  "path": ".".join(sig_name.split('.')[:-1]),
                  "name": sig_name.split(".")[-1],
                  "value": ("'b0", "0ns")
                  }
        self.vcd_file_contents = self.vcd_file_contents + "$var {} {} {} {} {} $end\n".format(
            signal["type"],
            signal["size"],
            signal["symbol"],
            signal["name"],
            signal["size"])
        self.signals[signal["name"]] = signal

    def add_clock_signal(self, clk_name, period):
        for s in self.signals.iteritems():
            hdl_path = s['path'] + '.' + s["name"]
            if hdl_path == clk_name:
                s["type"] = "clock"
                s["period"] = period
                return

    def add_transition(self, sig_name, value, time):
        for s in self.signals.iteritems():
            hdl_path = s['path'] + '.' + s["name"]
            if hdl_path == sig_name:
                s['value'].append((value, time))
                return

    #################################################################################################
    # VCD Import Functionality
    def parse_vcd_header(self):
        header = {
            'comment': self._get_vcd_header_item("comment"),
            'date': self._get_vcd_header_item("date"),
            'timescale': self._get_vcd_header_item("timescale")
        }
        return header

    def read_vcd_header(self):
        hdr = ""
        for line in self.vcd_file_contents:
            hdr = hdr + line
            if "$dumpvars" in line.lower():
                return hdr

    def _get_vcd_header_item(self, item_name):
        item_flag = False
        for line in self.vcd_file_contents:
            line = line.strip()
            if item_name in line.lower():
                item_flag = True
                if line.endswith("end"):  # Single line,
                    return line.split(' ')[-2]
            elif item_flag is True:
                return line
            elif "enddefinitions" in line.lower():
                raise ("Couldn't find " + item_name + "in vcd header")

    def _get_vcd_timescale(self):
        timescale_flag = False
        for line in self.vcd_file_contents:
            line = line.strip()
            if 'timescale' in line:
                timescale_flag = True
                if "end" in line:  # Single line,
                    m = re.match("\$timescale\s+(\d+)\s*([munpf]s)\s+\$end", line)
                    time = m.group(1)
                    scale = m.group(2)
                    print "// Timescale is : {}{}".format(time, scale)
                    return time, scale
            elif timescale_flag:
                time = int(line[0:-2])
                scale = line[-2:]
                return time, scale
        raise ValueError("Could not find timescale directive in VCD file")

    # TODO: decode the date and comment
    # TODO: decode the initial values
    def _decode_definition(self):
        self.signals = {}
        path = ""
        for line in self.vcd_file_contents:
            if line.startswith("$scope"):
                path = path + "." + line.split(' ')[2]
            if line.startswith("$var"):
                var = line.split(' ')[1:-1]
                signal = {"type": var[0], "size": int(var[1]), "symbol": var[2], "path": path, "name": var[3],
                          "value": "'b0"}
                self.signals[signal['name']] = signal
            if line.startswith("$upscope"):
                path = ".".join(path.split(".")[:-1])
            if 'enddefinitions' in line:
                return
        raise ValueError("Could not find enddefinitions directive in VCD file");

    def _symbol_to_name(self, sym):
        for sig_name in self.signals:
            if self.signals[sig_name]['symbol'] == sym:
                return sig_name

    def _decode_vcd_line(self, line):
        if line[0] == '#':
            self.timestamp = convert_time_unit(line[1:].strip() + self.scale, self.timeunit)
        elif ((line.find('$end') == 0) or
              (line.find('$dumpvars') == 0)):
            return None
        elif line[0] == 'b':  # Bus
            signal_name = self._symbol_to_name(line.split()[1])
            self.signals[signal_name]['value'] = "'" + line.split()[0]
            return signal_name
        else:  # Single bit
            signal_name = self._symbol_to_name(line[1])
            try:
                self.signals[signal_name]['value'] = line[0]
            except:
                print "RAW:{}".format(line)
                print "{}, {}".format(signal_name, line[1])
                print self.signals[signal_name]
                asdf
            return signal_name

    # TODO: change_on should be a dictionary with signals with
    # TODO: name and value to trigger the func to be called.
    # TODO: Alternatively, call on signal any change.
    # TODO: A list of timestamp ranges to be active.
    def parse_vcd_vars(self, func, change_on=None, time_range=None):
        vars_changing = False
        for line in self.vcd_file_contents:
            if not vars_changing and 'enddefinitions' in line:
                vars_changing = True
            elif vars_changing and change_on is None:
                self._decode_vcd_line(line)
                func(self.signals, self.timestamp)
            elif vars_changing:
                updated_sig = self._decode_vcd_line(line)
                if updated_sig in change_on:
                    func(self.signals, self.timestamp)

    def __str__(self):
        mystr = ""
        for sig in self.signals:
            mystr = mystr + "{:4} => {:15}: {}\n".format(self.signals[sig]['symbol'], sig, self.signals[sig]['size'])
        return mystr


"""
Example function: This uses the vcd_utils to decode a vcd that contents APB signals.
"""


def apb_decode(apb_signals, timestamp):
    import rtl.utils as verilog_util

    sys.path.append("/hosted/projects2/prya/pyublx")

    psel = apb_signals['PSelxSI']['value']
    pwdata = apb_signals['PWDataxDI']['value']
    # prdata  = apb_signals['']['value']
    pwrite = apb_signals['PWritexSI']['value']
    paddr = apb_signals['PAddrxDI']['value']
    penable = apb_signals['PEnablexSI']['value']

    if penable == '1' and psel == '1':
        if pwrite == '1':
            print "{} : Write 0x{} to   0x{}".format(timestamp, verilog_util.to_hex_str(pwdata),
                                                     verilog_util.to_hex_str('0' + paddr))
        # else:
        #  print "{} : Read  0x{} from 0x{}".format(timestamp, verilog_util.to_hex_str(prdata), verilog_util.to_hex_str('0'+paddr))


if __name__ == "__main__":
    # Check for the right version of python
    commandLine = argparse.ArgumentParser(description='Single step firmware/simulation tool for AMS VCD generation',
                                          usage='%(prog)s [options] <test case name>')
    commandLine.add_argument('vcd_file_name', help='Source VCD file to edit', action='store')

    opt = commandLine.parse_args()

    vcd = VCDFile("my_sample.vcd", True)
    vcd.add_new_var("blkA.blkB.sigA", "wire")
    vcd.add_new_var("blkA.blkB.sigB", "reg")
    vcd.add_new_var("blkA.clk", "reg")
    vcd.add_init_period("10ns")
    vcd.add_clock_signal("blkA.clk", "1ns")
    vcd.add_transition("blkA.blkB.sigA", "1", "15ns")
    vcd.add_transition("blkA.blkB.sigB", "0", "15ns")
    vcd.end_time("50ns")
    vcd.export_vcd()
