`timescale 1ns/1ps
`default_nettype none
// Concurrent assertions for Verilator --assert and AMD xsim. Icarus uses the
// procedural independent monitor because its concurrent SVA support is limited.
module context_sva(
 input wire clk,rst,
 input wire cpu_req_valid,cpu_req_ready,input wire[31:0]cpu_req_addr,
 input wire cpu_rsp_valid,cpu_rsp_ready,input wire[31:0]cpu_rsp_data,
 input wire mem_req_valid,mem_req_ready,input wire[31:0]mem_req_addr,
 input wire mem_rsp_valid,mem_rsp_ready,input wire[1:0]state
);
 assert property(@(posedge clk) disable iff(rst) mem_req_valid&&!mem_req_ready |=> mem_req_valid&&$stable(mem_req_addr));
 assert property(@(posedge clk) disable iff(rst) cpu_rsp_valid&&!cpu_rsp_ready |=> cpu_rsp_valid&&$stable(cpu_rsp_data));
 assert property(@(posedge clk) disable iff(rst) cpu_req_valid&&!cpu_req_ready |=> cpu_req_valid&&$stable(cpu_req_addr));
 assert property(@(posedge clk) disable iff(rst) mem_req_valid |-> mem_req_addr[3:0]==0);
 assert property(@(posedge clk) disable iff(rst) cpu_req_valid&&cpu_req_ready |-> cpu_req_addr[1:0]==0);
 assert property(@(posedge clk) disable iff(rst) state inside {2'd0,2'd1,2'd2});
 assert property(@(posedge clk) disable iff(rst) (state==1) |-> mem_req_valid);
 assert property(@(posedge clk) disable iff(rst) (state==2) |-> mem_rsp_ready);
 assert property(@(posedge clk) disable iff(rst) state==1&&!mem_req_ready |=> state==1);
 assert property(@(posedge clk) disable iff(rst) state==1&&mem_req_ready |=> state==2);
 assert property(@(posedge clk) disable iff(rst) state==2&&!mem_rsp_valid |=> state==2);
 assert property(@(posedge clk) disable iff(rst) state==2&&mem_rsp_valid |=> state==0);
endmodule
bind ai_cache_context context_sva bound_checks(.*);
`default_nettype wire
