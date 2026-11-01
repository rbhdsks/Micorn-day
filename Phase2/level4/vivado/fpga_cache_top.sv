`timescale 1ns/1ps
`default_nettype none
// Functional interface for out-of-context FPGA characterization.
// Debug counters are deliberately unconnected and may be optimized away.
module fpga_cache_top #(
 parameter INDEX_BITS=6, REGION_ENABLE=1, FEEDBACK_ENABLE=0, VICTIM_ENABLE=0
)(
 input wire clk,rst,prefetch_enable,
 input wire cpu_req_valid,output wire cpu_req_ready,input wire [31:0]cpu_req_addr,
 output wire cpu_rsp_valid,input wire cpu_rsp_ready,output wire[31:0]cpu_rsp_data,
 output wire mem_req_valid,input wire mem_req_ready,output wire[31:0]mem_req_addr,
 input wire mem_rsp_valid,output wire mem_rsp_ready,input wire[127:0]mem_rsp_data
);
 ai_cache_context #(.INDEX_BITS(INDEX_BITS),.REGION_ENABLE(REGION_ENABLE),
  .FEEDBACK_ENABLE(FEEDBACK_ENABLE),.VICTIM_ENABLE(VICTIM_ENABLE)) cache(
  .clk(clk),.rst(rst),.prefetch_enable(prefetch_enable),
  .cpu_req_valid(cpu_req_valid),.cpu_req_ready(cpu_req_ready),.cpu_req_addr(cpu_req_addr),
  .cpu_rsp_valid(cpu_rsp_valid),.cpu_rsp_ready(cpu_rsp_ready),.cpu_rsp_data(cpu_rsp_data),
  .mem_req_valid(mem_req_valid),.mem_req_ready(mem_req_ready),.mem_req_addr(mem_req_addr),
  .mem_rsp_valid(mem_rsp_valid),.mem_rsp_ready(mem_rsp_ready),.mem_rsp_data(mem_rsp_data),
  .stat_access(),.stat_hit(),.stat_miss(),.stat_pf_issued(),.stat_pf_useful(),
  .stat_pf_unused(),.stat_buffer_hit(),.stat_pf_late(),.stat_pf_suppressed()
 );
endmodule
`default_nettype wire
