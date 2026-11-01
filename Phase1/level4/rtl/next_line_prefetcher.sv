`timescale 1ns/1ps
// Reference policy: one following line per distinct accepted demand line.
// Repeated words do not generate duplicate candidates. No address wraparound.
module next_line_prefetcher (
 input wire clk, rst, enable, observe,
 input wire [27:0] line_addr,
 output reg candidate_valid,
 output reg [27:0] candidate_line
);
 reg seen;
 reg [27:0] last_line;
 always @(posedge clk) begin
  if(rst) begin
   seen<=0; last_line<=0; candidate_valid<=0; candidate_line<=0;
  end else begin
   candidate_valid<=0;
   if(observe && (!seen || line_addr!=last_line)) begin
    seen<=1; last_line<=line_addr;
    if(enable && line_addr!=28'hfffffff) begin
     candidate_valid<=1; candidate_line<=line_addr+28'd1;
    end
   end
  end
 end
endmodule
