`timescale 1ns/1ps
// Simulation-only deterministic backing store, variable request/response delay.
module dram_model #(parameter LATENCY=12)(
 input wire clk,rst, req_valid, output wire req_ready,
 input wire [31:0] req_addr, output reg rsp_valid,
 input wire rsp_ready, output reg [127:0] rsp_data,
 output reg [31:0] reads
);
 reg busy;
 reg [31:0] address;
 integer remaining, tick, j;
 function automatic [31:0] word_at(input [31:0] a);
  word_at=(a>>2)^32'hcafe1234;
 endfunction
 assign req_ready=!rst && !busy && !rsp_valid && tick%5!=0;
 always @(posedge clk) begin
  if(rst) begin busy<=0; rsp_valid<=0; rsp_data<=0; reads<=0; remaining<=0; tick<=0; address<=0; end
  else begin
   tick<=tick+1;
   if(rsp_valid && rsp_ready) rsp_valid<=0;
   if(req_valid && req_ready) begin
    busy<=1; remaining<=LATENCY+(req_addr[6:4]%3); address<=req_addr; reads<=reads+1;
   end
   if(busy) begin
    if(remaining==0) begin
     for(j=0;j<4;j=j+1) rsp_data[j*32 +:32]<=word_at(address+4*j);
     rsp_valid<=1; busy<=0;
    end else remaining<=remaining-1;
   end
  end
 end
endmodule
