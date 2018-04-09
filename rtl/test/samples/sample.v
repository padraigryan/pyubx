//-----------------------------------------------------------------------------
// Company    : u-blox Cork, Ireland
// Created    : 2014-11
// Last commit: $Date: 2016/08/19 $
// Updated by : $Author: prya $
//-----------------------------------------------------------------------------
// Copyright (c) 2014 u-blox Cork, Ireland
//-----------------------------------------------------------------------------
// $Id: //depot/icm/proj/ic_aux_dig_if/gottardo/rtl/aux_dig_if/aux_clk_mux_rst_sync.v#2 $
//-----------------------------------------------------------------------------
//
//-----------------------------------------------------------------------------
// 1) Resync the resets onto the relevant clock domains (bypassable)
// 2) Muxing of functional and test clocks
//-----------------------------------------------------------------------------

module aux_clk_mux_rst_sync(

  PClkxCI,
  PResetxARBI,
  I_adcClkOut,
  CHI1adcCalClk,
  CHI1adcP2CalClk,
  CHI2adcCalClk,
  CHI2adcP2CalClk,
  ShiftClkxCI,
  ScanTestModexTI,
  scan_test_mode,
  ScanResetxRBI,
  master_ld_mmap,
  EnablesAdc_i_enxI,
  CHI_adcEn,
  CHI1_chEn,
  CHI1_calMode,
  CHI1_short,
  CHI2_chEn,
  CHI2_calMode,
  CHI2_short,
  adc_iqmuxEn_i,
  aux_dfe_clk_in,

  PResetxRBI,
  master_ld_mmap_muxed,
  I_adcClkOut_muxed,
  CHI1adcCalClk_muxed,
  CHI1adcP2CalClk_muxed,
  CHI2adcCalClk_muxed,
  CHI2adcP2CalClk_muxed,
  CHI_adcEn_muxed,
  CHI1_chEn_muxed,
  CHI1_calMode_muxed,
  CHI1_short_muxed,
  CHI2_chEn_muxed,
  CHI2_calMode_muxed,
  CHI2_short_muxed,
  adc_iqmuxEn_i_muxed,
  EnablesAdc_i_enxI_muxed,
  aux_dfe_clk_out
);

  // Source clocks
  input                       PClkxCI,I_adcClkOut;
  input                       CHI1adcCalClk, CHI1adcP2CalClk;
  input                       CHI2adcCalClk;
  input                       CHI2adcP2CalClk;
  input                       aux_dfe_clk_in;

  // Scan Test interface
  input                       ShiftClkxCI;
  input                       ScanTestModexTI;
  output                      scan_test_mode;
  input                       ScanResetxRBI;

  // Source resets/signals
  input                       PResetxARBI;
  input                       master_ld_mmap;
  input                       EnablesAdc_i_enxI;

  // Mux'ed inputs
  output                      CHI_adcEn;
  output                      CHI1_chEn;
  output  [5:4]               CHI1_calMode;
  output                      CHI1_short;
  output                      CHI2_chEn;
  output  [1:0]            CHI2_calMode;
  output                      CHI2_short;
  output                      adc_iqmuxEn_i;

  // resync'ed resets/signals
  output                      PResetxRBI;
  output                      master_ld_mmap_muxed;
  output                      EnablesAdc_i_enxI_muxed;

  // Mux'ed clock outputs
  output                      I_adcClkOut_muxed;
  output                      CHI1adcCalClk_muxed;
  output                      CHI1adcP2CalClk_muxed;
  output                      CHI2adcCalClk_muxed;
  output                      CHI2adcP2CalClk_muxed;
  output                      aux_dfe_clk_out;

  // Mux'ed outputs
  input                       CHI_adcEn_muxed;
  input                       CHI1_chEn_muxed;
  input [1:0]                 CHI1_calMode_muxed;
  input                       CHI1_short_muxed;
  input                       CHI2_chEn_muxed;
  input [1:0]                 CHI2_calMode_muxed;
  input                       CHI2_short_muxed;
  input                       adc_iqmuxEn_i_muxed;

  parameter ENABLE_LOCAL_RSTB_RESYNC = 1;
  parameter ENABLE_LOCAL_CLK_MUX     = 1;

  // Internal wiring
  wire                       PResetxARBI_int; 

  ///////////////////////////////////////////////////////////////////////////////
  // Asynchronous reset/signal resync'ing
  assign EnablesAdc_i_enxI_muxed  =  ScanTestModexTI ? ScanResetxRBI : EnablesAdc_i_enxI;
  
  assign scan_test_mode           = ScanTestModexTI;

  ///////////////////////////////////////////////////////////////////////////////
  // Hold sensitive signal to a safe value during scan mode.
  assign CHI_adcEn              = ScanTestModexTI ? 1'b1 : CHI_adcEn_muxed;

  assign CHI1_chEn              = ScanTestModexTI ? 1'b0 : CHI1_chEn_muxed;
  assign CHI1_calMode           = ScanTestModexTI ? 2'b00: CHI1_calMode_muxed;
  assign CHI1_short             = ScanTestModexTI ? 1'b0 : CHI1_short_muxed;
  assign CHI2_chEn              = ScanTestModexTI ? 1'b0 : CHI2_chEn_muxed;
  assign CHI2_calMode           = ScanTestModexTI ? 2'b00: CHI2_calMode_muxed;
  assign CHI2_short             = ScanTestModexTI ? 1'b0 : CHI2_short_muxed;
  assign adc_iqmuxEn_i          = ScanTestModexTI ? 1'b0 : adc_iqmuxEn_i_muxed;
 
  task convert;
    input [7:0] tmp_in;
    output [7:0] tmpout;

    begin
      tmpout = (9.5) * (tmp_in +33)
    end
  endtask

  ///////////////////////////////////////////////////////////////////////////////
  // Mux the Resets
  generate

    if (ENABLE_LOCAL_RSTB_RESYNC == 1'b1) begin

      assign PResetxARBI_int = ScanTestModexTI ? ScanResetxRBI : PResetxARBI;

      reset_sync PResetxRBI_sync_i(
            .rst_n_o                          (PResetxRBI),
            .rst_an_i                         (PResetxARBI_int),
            .clk                              (PClkxCI),
            .rst_sync_bypass                  (ScanTestModexTI)                    // Note; bypass pointless becuase of previous mux. 
            );

    end else begin
      
      assign PResetxRBI = PResetxARBI;                                       // Resync'ed and scan mux'ed in the CCURCU

    end

  endgenerate

  ///////////////////////////////////////////////////////////////////////////////
  // Resync the master load signal
  signal_sync master_ld_pclk_i(
        .rst_n                            (PResetxRBI),
        .clk                              (PClkxCI),
        .async_i                          (master_ld_mmap),
        .sync_o                           (master_ld_mmap_muxed)
        );

  ///////////////////////////////////////////////////////////////////////////////
  // The DFE clock is passed straight through a scan mux
  clockmux2   aux_dfe_clk_mux(
      .clkout                             (aux_dfe_clk_out), 
      .clkin1                             (aux_dfe_clk_in), 
      .clkin2                             (ShiftClkxCI), 
      .clksel                             (ScanTestModexTI)
      );

  clockmux2   I_adcClkOut_mux(
      .clkout                             (I_adcClkOut_muxed), 
      .clkin1                             (I_adcClkOut), 
      .clkin2                             (ShiftClkxCI), 
      .clksel                             (ScanTestModexTI)
      );

  clockmux2  CHI1adcCalClk_mux (
      .clkout                             (CHI1adcCalClk_muxed), 
      .clkin1                             (CHI1adcCalClk), 
      .clkin2                             (ShiftClkxCI), 
      .clksel                             (ScanTestModexTI)
      );

  clockmux2 CHI1adcP2CalClk_mux  (
      .clkout                             (CHI1adcP2CalClk_muxed), 
      .clkin1                             (CHI1adcP2CalClk), 
      .clkin2                             (ShiftClkxCI), 
      .clksel                             (ScanTestModexTI)
      );

  clockmux2 CHI2adcCalClk_mux(
      .clkout                             (CHI2adcCalClk_muxed), 
      .clkin1                             (CHI2adcCalClk), 
      .clkin2                             (ShiftClkxCI), 
      .clksel                             (ScanTestModexTI)
      );

  clockmux2 CHI2adcP2CalClk_mux(
      .clkout                             (CHI2adcP2CalClk_muxed), 
      .clkin1                             (CHI2adcP2CalClk), 
      .clkin2                             (ShiftClkxCI), 
      .clksel                             (ScanTestModexTI)
      );

endmodule
