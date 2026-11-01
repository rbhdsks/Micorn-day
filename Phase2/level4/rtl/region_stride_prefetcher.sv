`timescale 1ns/1ps
`default_nettype none
// Bounded address-region history. Context is address locality, not program meaning.
module region_stride_prefetcher #(
 parameter ENTRIES=4, parameter REGION_LINE_BITS=8
)(
 input wire clk, rst, enable, observe,
 input wire [27:0] line_addr,
 output reg candidate_valid,
 output reg [27:0] candidate_line
);
 localparam KEY_BITS=28-REGION_LINE_BITS;
 localparam PTR_BITS=ENTRIES>1 ? $clog2(ENTRIES) : 1;
 reg valid[0:ENTRIES-1];
 reg [KEY_BITS-1:0] region[0:ENTRIES-1];
 reg [27:0] last_line[0:ENTRIES-1];
 reg signed [28:0] stride[0:ENTRIES-1];
 reg [1:0] confidence[0:ENTRIES-1];
 reg [PTR_BITS-1:0] replace_ptr;
 integer match_slot,free_slot,j;
 logic [PTR_BITS-1:0] allocation_slot;
 reg signed [28:0] delta;
 reg signed [29:0] predicted;
 always_comb begin
  match_slot=-1; free_slot=-1;
  for(integer k=0;k<ENTRIES;k=k+1) begin
   if(valid[k] && region[k]==line_addr[27:REGION_LINE_BITS]) match_slot=k;
   if(!valid[k] && free_slot<0) free_slot=k;
  end
  allocation_slot=free_slot>=0 ? PTR_BITS'(free_slot) : replace_ptr;
  delta=0;predicted=0;
  if(match_slot>=0) begin
   delta=$signed({1'b0,line_addr})-$signed({1'b0,last_line[match_slot]});
   predicted=$signed({2'b0,line_addr})+$signed(stride[match_slot]);
  end
 end
 always_ff @(posedge clk) begin
  if(rst) begin
   candidate_valid<=0;candidate_line<=0;replace_ptr<=0;
   for(j=0;j<ENTRIES;j=j+1) valid[j]<=0;
  end else begin
   candidate_valid<=0;
   if(observe) begin
    if(match_slot<0) begin
     valid[allocation_slot]<=1;region[allocation_slot]<=line_addr[27:REGION_LINE_BITS];
     last_line[allocation_slot]<=line_addr;stride[allocation_slot]<=0;confidence[allocation_slot]<=0;
     if(free_slot<0) replace_ptr<=replace_ptr==PTR_BITS'(ENTRIES-1) ? {PTR_BITS{1'b0}} : replace_ptr+1'b1;
    end else if(line_addr!=last_line[match_slot]) begin
     last_line[match_slot]<=line_addr;
     if(delta==stride[match_slot] && delta!=0) begin
      if(confidence[match_slot]!=3) confidence[match_slot]<=confidence[match_slot]+1'b1;
      if(enable && confidence[match_slot]>=1 && predicted>=0 && predicted<30'sh10000000) begin
       candidate_valid<=1;candidate_line<=predicted[27:0];
      end
     end else begin stride[match_slot]<=delta;confidence[match_slot]<=1;end
    end
   end
  end
 end
 // synthesis translate_off
 initial begin
  if(ENTRIES<1 || REGION_LINE_BITS<1 || REGION_LINE_BITS>27)
   $fatal(1,"invalid region predictor configuration");
 end
 // synthesis translate_on
endmodule

`default_nettype wire
