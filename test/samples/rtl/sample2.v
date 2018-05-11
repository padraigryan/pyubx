//-----------------------------------------------------------------------------
// Company    : u-blox Cork, Ireland
// Created    : Monday, 02 March 2015 08:48PM
// Last commit: $Date: 2015/06/04 $
// Updated by : $Author: prya $
//-----------------------------------------------------------------------------
// Copyright (c) 2014 u-blox Cork, Ireland
//-----------------------------------------------------------------------------
// $Id: //depot/icm/proj/ic_mx_dig_top/trunk/rtl/mx_dig_top/mx_apb_mmap.v#5 $
//-----------------------------------------------------------------------------

module mx_apb_mmap(
  input sig1,sig2, sig3,            // these types of ports don't work yet
  sig4, sig5;
	input   wire                PClkxCI,
	input                   PResetxARBI,
	output reg              PEnClkxSO,
	input                   PEnClkxSI,
	input           [31:2]  PAddrxDI,
	input                   PSelxSI,
	input                   PEnablexSI,
	input                   PWritexSI,
	input           [31:0]  PWDataxDI,
	output  reg             PReadyxSO,
	output  reg     [31:0]  PRDataxDO,
	output  reg             PSlverrxSO,
	output                  Meas_ldoBypassxO,           // this is a comment
	output                  Meas_ldoEnablexO,/// I'm a comment too
// I'm just in the way  
	output                  Meas_ldoFast_lockxO,
	input           [15:0]  Hist_q_5Hist_out_i_10xI,
	input /*important shit to be said*/          [15:0]  Hist_q_5Hist_out_i_11xI,
	input           [15:0]  Hist_q_6Hist_out_i_12xI,
	input           [15:0]  Hist_q_6Hist_out_i_13xI,
  /* howa
   * about 
   here then
   adsf */
	input           [15:0]  Hist_q_7Hist_out_i_14xI,
	input           [15:0]  Hist_q_7Hist_out_i_15xI,
	input           [15:0]  Hist_q_8Hist_out_i_16xI,
	input           [15:0]  Hist_q_8Hist_out_i_17xI,
	input           [15:0]  Hist_q_9Hist_out_i_18xI,
/*asdf*/

	input           [15:0]  Hist_q_9Hist_out_i_19xI,
	input           [15:0]  Hist_q_10Hist_out_i_20xI,
	input           [15:0]  Hist_q_10Hist_out_i_21xI,
	input           [15:0]  Hist_q_11Hist_out_i_22xI,input           [15:0]  Hist_q_11Hist_out_i_23xI,
	input           [15:0]  Hist_q_12Hist_out_i_24xI,	input           [15:0]  Hist_q_12Hist_out_i_25xI,
	input           [15:0]  Hist_q_13Hist_out_i_26xI,
	input           [15:0]  Hist_q_13Hist_out_i_27xI,
	input           [15:0]  Hist_q_14Hist_out_i_28xI,
	input           [15:0]  Hist_q_14Hist_out_i_29xI,
	input           [15:0]  Hist_q_15Hist_out_i_30xI,
	input           [15:0]  Hist_q_15Hist_out_i_31xI,output           [3:0]  Adc_tmodeTmodexO
  );

  reg           PSelxSI_meas;
  reg           PSelxSI_measADC;
  reg           PSelxSI_measADCflags;
  reg           PSelxSI_measDFE;
 
  wire          PEnClkxSO_meas, PEnClkxSO_measADC, PEnClkxSO_measDFE, PEnClkxSO_measADCflags;
  wire          PReadyxSO_meas, PReadyxSO_measADC, PReadyxSO_measDFE, PReadyxSO_measADCflags;
  wire [31:0]   PRDataxDO_meas, PRDataxDO_measADC, PRDataxDO_measDFE, PRDataxDO_measADCflags;
  wire          PSlverrxSO_meas, PSlverrxSO_measADC, PSlverrxSO_measDFE, PSlverrxSO_measADCflags;
endmodule

module second_mod ( 
ipsig, outsig, bidsig, inbus,
outbus, bidrbus);

input ipsig;
output  outsig;
inout bidsig;
input [4:3] inbus;
output [3:4] outbus;
inout [0:0] bidrbus;


endmodule

