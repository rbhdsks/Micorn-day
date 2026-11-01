`timescale 1ns/1ps
// Single-stream line-stride predictor. Trains only on distinct demand lines.
module stride_prefetcher (
 input wire clk, rst, enable, observe,
 input wire [27:0] line_addr,
 output reg candidate_valid,
 output reg [27:0] candidate_line
);
 reg seen;
 reg [27:0] last_line;
 reg signed [28:0] stride;
 reg [1:0] confidence;
 wire signed [28:0] delta = $signed({1'b0,line_addr})-$signed({1'b0,last_line});
 wire signed [29:0] predicted = $signed({2'b0,line_addr}) + $signed(stride);
 always @(posedge clk) begin
  if (rst) begin
   seen<=0; last_line<=0; stride<=0; confidence<=0;
   candidate_valid<=0; candidate_line<=0;
  end else begin
   candidate_valid<=0;
   if (observe && (!seen || line_addr!=last_line)) begin
    seen<=1; last_line<=line_addr;
    if (!seen) begin stride<=0; confidence<=0; end
    else if (delta==stride && delta!=0) begin
     if (confidence!=3) confidence<=confidence+1'b1;
     // Two matching deltas required. Reject address-space wraparound.
     if (enable && confidence>=1 && predicted>=0 && predicted<30'sh10000000) begin
      candidate_valid<=1; candidate_line<=predicted[27:0];
     end
    end else begin stride<=delta; confidence<=1; end
   end
  end
 end
endmodule
