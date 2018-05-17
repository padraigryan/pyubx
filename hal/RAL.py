#!/usr/bin/env python
import sys
import os
import pickle

from RAL_base import *
from RAL_block import *

__RAL_VERSION__ = 1

class RAL(RAL_base):
  
  def __init__(self,  pkl_file = ".mem_map.dat", force_rebuild = False):
    if os.path.exists(pkl_file) == False or force_rebuild == True:
      self.rebuild_mem_map(pkl_file)
    else:
      print "INFO: Restoring Memory Map from file : " + pkl_file
      (ver, self.ral_item) = pickle.load(open(pkl_file, "rb"))
      if(ver != __RAL_VERSION__):
        self.rebuild_mem_map(pkl_file)


  def rebuild_mem_map(self,  pkl_file = ".mem_map.dat"):
    RAL_base.__init__(self, "RAL")
    try:
      workspace = os.environ['WORKSPACE']
    except:
      print "ERROR: WORKSPACE not set"
    """
    #############################################################################
    ## Config Registers
    self.add_item(RAL_subblock(  0x40000000, workspace + '/meta/config_registers/config_regs.xlsx', 'Sheet1', 'config' ) )

    #############################################################################
    ## RX Path
    path_to_reg_file = workspace + '/meta/rx_dig_top/'
    
    rxdfe = RAL_subblock( 0x40002000, path_to_reg_file + 'rx_apb_mmap_rxdfe.xlsx', 'RxDFE', 'RxDFE')
    rxadc = RAL_subblock( 0x40002400, path_to_reg_file + 'rx_apb_mmap_rxadc.xlsx', 'RxADC', 'RxADC')
    rxrf  = RAL_subblock( 0x40002800, path_to_reg_file + 'rx_apb_mmap_rxrf.xlsx',  'RxRF',  'RxRF')
    rxbb  = RAL_subblock( 0x40002C00, path_to_reg_file + 'rx_apb_mmap_rxbb.xlsx',  'RxBB',  'RxBB')
    self.add_item(RAL_block([rxdfe, rxadc, rxrf, rxbb], "rx1", 0x40002000))

    rxdfe = RAL_subblock( 0x40004000, path_to_reg_file + 'rx_apb_mmap_rxdfe.xlsx', 'RxDFE', 'RxDFE')
    rxadc = RAL_subblock( 0x40004400, path_to_reg_file + 'rx_apb_mmap_rxadc.xlsx', 'RxADC', 'RxADC')
    rxrf  = RAL_subblock( 0x40004800, path_to_reg_file + 'rx_apb_mmap_rxrf.xlsx',  'RxRF',  'RxRF')
    rxbb  = RAL_subblock( 0x40004C00, path_to_reg_file + 'rx_apb_mmap_rxbb.xlsx',  'RxBB',  'RxBB')
    self.add_item(RAL_block([rxdfe, rxadc, rxrf, rxbb], "rx2", 0x40004000))

    rxdfe = RAL_subblock( 0x40006000, path_to_reg_file + 'rx_apb_mmap_rxdfe.xlsx', 'RxDFE', 'RxDFE')
    rxadc = RAL_subblock( 0x40006400, path_to_reg_file + 'rx_apb_mmap_rxadc.xlsx', 'RxADC', 'RxADC')
    rxrf  = RAL_subblock( 0x40006800, path_to_reg_file + 'rx_apb_mmap_rxrf.xlsx',  'RxRF',  'RxRF')
    rxbb  = RAL_subblock( 0x40006C00, path_to_reg_file + 'rx_apb_mmap_rxbb.xlsx',  'RxBB',  'RxBB')
    self.add_item(RAL_block([rxdfe, rxadc, rxrf, rxbb], "rx3", 0x40006000))

    rxdfe = RAL_subblock( 0x40008000, path_to_reg_file + 'rx_apb_mmap_rxdfe.xlsx', 'RxDFE', 'RxDFE')
    rxadc = RAL_subblock( 0x40008400, path_to_reg_file + 'rx_apb_mmap_rxadc.xlsx', 'RxADC', 'RxADC')
    rxrf  = RAL_subblock( 0x40008800, path_to_reg_file + 'rx_apb_mmap_rxrf.xlsx',  'RxRF',  'RxRF')
    rxbb  = RAL_subblock( 0x40008C00, path_to_reg_file + 'rx_apb_mmap_rxbb.xlsx',  'RxBB',  'RxBB')
    self.add_item(RAL_block([rxdfe, rxadc, rxrf, rxbb], "rx4", 0x40008000))

    #############################################################################
    ## TX Path
    path_to_reg_file = workspace + '/meta/tx_dig_top/'

    txdfe1 = RAL_subblock( 0x4000A000, path_to_reg_file + 'tx_apb_mmap_txdfe1.xls', 'TxDFE1', 'TxDFE1' )
    txdfe2 = RAL_subblock( 0x4000A200, path_to_reg_file + 'tx_apb_mmap_txdfe2.xls', 'TxDFE2', 'TxDFE2' )
    txrf   = RAL_subblock( 0x4000A400, path_to_reg_file + 'tx_apb_mmap_txrf.xls',   'TxRF',   'TxRF')
    txbb   = RAL_subblock( 0x4000A600, path_to_reg_file + 'tx_apb_mmap_txbb.xls',   'TxBB',   'TxBB')
    self.add_item(RAL_block([txdfe1,txdfe2, txrf, txbb], 'tx1', 0x4000A000))

    txdfe1 = RAL_subblock( 0x4000C000, path_to_reg_file + 'tx_apb_mmap_txdfe1.xls', 'TxDFE1', 'TxDFE1' )
    txdfe2 = RAL_subblock( 0x4000C200, path_to_reg_file + 'tx_apb_mmap_txdfe2.xls', 'TxDFE2', 'TxDFE2' )
    txrf   = RAL_subblock( 0x4000C400, path_to_reg_file + 'tx_apb_mmap_txrf.xls',   'TxRF',   'TxRF')
    txbb   = RAL_subblock( 0x4000C600, path_to_reg_file + 'tx_apb_mmap_txbb.xls',   'TxBB',   'TxBB')
    self.add_item(RAL_block([txdfe1,txdfe2, txrf, txbb], 'tx2', 0x4000C000))

    #############################################################################
    ## MX Path
    path_to_reg_file = workspace + '/meta/mx_dig_top/'

    mxmeas     = RAL_subblock( 0x4000E000, path_to_reg_file + 'mx_apb_mmap_meas.xlsx',    'Meas',     'Meas' )
    mxadc      = RAL_subblock( 0x4000E800, path_to_reg_file + 'mx_apb_mmap_measADC.xlsx', 'MeasADC',  'MeasADC' )
    mxdfe      = RAL_subblock( 0x4000F000, path_to_reg_file + 'mx_apb_mmap_measDFE.xlsx', 'MeasDFE',  'MeasDFE' )
    mxadcflags = RAL_subblock( 0x4000F800, path_to_reg_file + 'mx_apb_mmap_measADCflags.xlsx', 'MeasADCflags', 'MeasADCflags' )
    self.add_item(RAL_block([mxmeas, mxadc, mxdfe, mxadcflags], "mx1", 0x4000E000))


    mxmeas     = RAL_subblock( 0x40010000, path_to_reg_file + 'mx_apb_mmap_meas.xlsx',    'Meas',     'Meas' )
    mxadc      = RAL_subblock( 0x40010800, path_to_reg_file + 'mx_apb_mmap_measADC.xlsx', 'MeasADC',  'MeasADC' )
    mxdfe      = RAL_subblock( 0x40011000, path_to_reg_file + 'mx_apb_mmap_measDFE.xlsx', 'MeasDFE',  'MeasDFE' )
    mxadcflags = RAL_subblock( 0x40011800, path_to_reg_file + 'mx_apb_mmap_measADCflags.xlsx', 'MeasADCflags', 'MeasADCflags' )
    self.add_item(RAL_block([mxmeas, mxadc, mxdfe, mxadcflags], "mx2", 0x40010000))

    #############################################################################
    ## Aux Path
    path_to_reg_file = workspace + '/meta/aux_dig_top/'

    auxTop       = RAL_subblock( 0x40012000,                      path_to_reg_file + 'aux_apb_mmap.xlsx', 'AuxTop', 'AuxTop' )
    auxADC       = RAL_subblock( 0x40012000 + auxTop.last_offset, path_to_reg_file + 'aux_apb_mmap.xlsx', 'AuxADC', 'AuxADC' )
    auxDFE       = RAL_subblock( 0x40012000 + auxADC.last_offset, path_to_reg_file + 'aux_apb_mmap.xlsx', 'AuxDFE', 'AuxDFE' )
    auxADC_flags = RAL_subblock( 0x40012000 + auxDFE.last_offset, path_to_reg_file + 'aux_apb_mmap.xlsx', 'AuxADC_flags', 'AuxADC_flags' )

    self.add_item(auxTop)
    self.add_item(auxADC)
    self.add_item(auxDFE)
    self.add_item(auxADC_flags)

    self.add_item(RAL_block([auxTop, auxADC, auxDFE, auxADC_flags], "aux", 0x40012000))

    #############################################################################
    ## TX SYN Path
    path_to_reg_file = workspace + '/meta/pll_dig_top/'

    synth = RAL_subblock( 0x40014000,                     path_to_reg_file + 'pll_apb_mmap.xlsx', 'synth', 'synth' )
    vco   = RAL_subblock( 0x40014000 + synth.last_offset, path_to_reg_file + 'pll_apb_mmap.xlsx', 'vco', 'vco' )
    bias  = RAL_subblock( 0x40014000 + vco.last_offset,   path_to_reg_file + 'pll_apb_mmap.xlsx', 'bias', 'bias' )
    spare = RAL_subblock( 0x40014000 + bias.last_offset,  path_to_reg_file + 'pll_apb_mmap.xlsx', 'spare','spare' )

    self.add_item(RAL_block([synth, vco, bias, spare], "pll1", 0x40014000))
    self.add_item(RAL_block([synth, vco, bias, spare], "pll2", 0x40016000))
    self.add_item(RAL_block([synth, vco, bias, spare], "pll3", 0x40018000))
    #############################################################################
    ## RFFE
    path_to_reg_file = workspace + '/meta/rffe/'

    rffe1 = RAL_subblock( 0x4001A000, path_to_reg_file + 'rffe_regs.xlsx', 'Sheet1', 'rffe1' )
    rffe2 = RAL_subblock( 0x4001C000, path_to_reg_file + 'rffe_regs.xlsx', 'Sheet1', 'rffe2' )

    self.add_item(rffe1)
    self.add_item(rffe2)
    """
    #############################################################################
    ## Scratch pad
    path_to_reg_file = workspace + '/meta/ic_tx_scratch_ram/'
    txscratch  = RAL_subblock( 0x4001E000, path_to_reg_file + 'txscratch_regs.xlsx', 'Sheet1', 'txscratch' )

    path_to_reg_file = workspace + '/meta/ic_rx_scratch_ram/'
    rx1scratch = RAL_subblock( 0x40020000, path_to_reg_file + 'rxscratch_regs.xlsx', 'Sheet1', 'rx1scratch' )
    rx2scratch = RAL_subblock( 0x40022000, path_to_reg_file + 'rxscratch_regs.xlsx', 'Sheet1', 'rx2scratch' )

    self.add_item(txscratch)
    self.add_item(rx1scratch)
    self.add_item(rx2scratch)

    #############################################################################
    ## Scheduler Registers
    self.add_item(RAL_subblock(  0x40024000,  workspace + '/meta/sch/sch_regs.xlsx', 'Sheet1', 'sch' ))

    #############################################################################
    ## Watch Dog Timer Registers
    self.add_item(RAL_subblock(  0x40026000,  workspace + '/code/registers/xls/WDG.xlsx', 'SheetB', 'wdt' ) )

    #############################################################################
    ## Timer Registers
    self.add_item(RAL_subblock(  0x40028000,  workspace + '/code/registers/xls/Timer.xlsx', 'SheetB', 'timer' )  )

    #############################################################################
    ## UART Registers
    self.add_item(RAL_subblock(  0x4002A000, workspace + '/doc/uart/UART.xlsx', 'SheetB', 'uart' ) )
    
    #############################################################################
    ## GPIO Registers
    self.add_item(RAL_subblock(  0x4002E000, workspace + '/meta/pio/pio_regs.xlsx', 'Sheet1', 'gpio' ) )

   
    #############################################################################
    ## Timestamp Manager Registers
    self.add_item(RAL_subblock(  0x40030000, workspace + '/meta/ts_mgr/ts_mgr_regs.xlsx', 'Sheet1', 'ts' ) )

    #############################################################################
    ## OTP Registers
    self.add_item(RAL_subblock(  0x40032000, workspace + '/code/registers/xls/OTP.xlsx', 'SheetB', 'otp' ) )

    #TODO: digrf????
    
    #############################################################################
    ## CCU_RCU Registers
    #self.add_item(RAL_subblock(  0x40038000, workspace + '/meta/ccu_rcu/ccu_rcu_csr.xlsx', 'clock_control_unit', 'ccu' ) )
    
    # Save the RAL to file for use later
    print "[INFO] Write memory map to file: " + pkl_file
    print self.display()
    pickle.dump((__RAL_VERSION__, self.ral_item), open(pkl_file, 'wb'))

  @classmethod
  def build(cls, pkl_file = ".mem_map.dat"):
    print "INFO: Rebuilding the register model"
    return cls(pkl_file, True)



  def __str__(self):
    blk_str = ""
    for (blk_name, blk) in self.ral_item.iteritems():
      blk_str = blk_str + ' ' + blk.label
    return blk_str

"""
Test program
"""
if __name__ == "__main__":  

  br = RAL()

  print br.uart.UART_SR.RXFIFO_NOTEMPTY()
  #
  # for i in range(0,4):
  #   myRal.rx1.RxBB.adc_ldo(0xDEADBEEF)
  #   myRal.rx1.RxBB.adc_ldo()
  #   myRal.rx1.RxBB.adc_ldo(0x00000000)
  #   myRal.rx1.RxBB.adc_ldo()
  #   myRal.rx1.RxBB.adc_ldo(0xFFFFFFFF)
  #   myRal.rx1.RxBB.adc_ldo()
