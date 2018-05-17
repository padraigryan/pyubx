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

module sample2(
  input sig1,sig2, sig3,            // these types of ports don't work yet
  sig4, sig5;
	input   wire                PClkxCI,   PResetxARBI,
	output reg              PEnClkxSO,
  /* howa
   * about 
   here then
   adsf */
	input                   PEnClkxSI,	input           [31:2]  PAddrxDI,
	input  /*important shit to be said*/   PSelxSI,
	input                   PEnablexSI,/// I'm a comment too
	input                   PWritexSI,
	input           [31:0]  PWDataxDI,
// I'm just in the way  
	output               PReadyxSO,           // this is a comment
	output  reg     [31:0]  PRDataxDO,
	output  logic             PSlverrxSO,
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

