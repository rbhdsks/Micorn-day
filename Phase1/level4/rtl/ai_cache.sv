`timescale 1ns/1ps
// Read-only cache, fixed 16-byte lines, one memory transaction outstanding.
// CPU hits can proceed while a speculative memory read is outstanding.
module ai_cache #(parameter INDEX_BITS=6, parameter PREFETCH_POLICY=1)(
 input wire clk, rst, prefetch_enable,
 input wire cpu_req_valid, output wire cpu_req_ready,
 input wire [31:0] cpu_req_addr,
 output reg cpu_rsp_valid, input wire cpu_rsp_ready,
 output reg [31:0] cpu_rsp_data,
 output wire mem_req_valid, input wire mem_req_ready,
 output wire [31:0] mem_req_addr,
 input wire mem_rsp_valid, output wire mem_rsp_ready,
 input wire [127:0] mem_rsp_data,
 output reg [31:0] stat_access, stat_hit, stat_miss,
 output reg [31:0] stat_pf_issued, stat_pf_useful, stat_pf_unused
);
 localparam N=1<<INDEX_BITS;
 localparam IDLE=0, SEND=1, WAIT=2;
 reg [1:0] state;
 reg [127:0] data [0:N-1];
 reg [27:0] tags [0:N-1];
 reg valid [0:N-1], prefetched [0:N-1];
 wire [27:0] req_line=cpu_req_addr[31:4];
 wire [INDEX_BITS-1:0] idx=req_line[INDEX_BITS-1:0];
 wire hit=valid[idx] && tags[idx]==req_line;
 reg demand_pending;
 reg [31:0] demand_addr;
 reg tx_prefetch;
 reg [27:0] tx_line;
 wire [INDEX_BITS-1:0] tx_idx=tx_line[INDEX_BITS-1:0];
 reg pf_pending;
 reg [27:0] pf_line;
 wire [INDEX_BITS-1:0] pf_idx=pf_line[INDEX_BITS-1:0];
 wire candidate_valid;
 wire [27:0] candidate_line;
 wire accept=cpu_req_valid && cpu_req_ready;
 assign cpu_req_ready=!rst && !demand_pending && (!cpu_rsp_valid || cpu_rsp_ready)
                       && !(state==WAIT && mem_rsp_valid);
 assign mem_req_valid=!rst && state==SEND;
 assign mem_req_addr={tx_line,4'b0};
 assign mem_rsp_ready=!rst && state==WAIT;
 // Same registered candidate interface and arbitration in both policies.
 // 1 = repeated-delta stride; 2 = next distinct demand line + 1.
 generate
  if(PREFETCH_POLICY==1) begin: g_stride
   stride_prefetcher predictor(clk,rst,prefetch_enable,accept,req_line,candidate_valid,candidate_line);
  end else begin: g_next_line
   next_line_prefetcher predictor(clk,rst,prefetch_enable,accept,req_line,candidate_valid,candidate_line);
  end
 endgenerate
 // Guard unsupported configurations during simulation; not part of hardware.
 // synthesis translate_off
 initial begin
  if(INDEX_BITS<1 || INDEX_BITS>27) $fatal(1,"INDEX_BITS must be in 1..27");
  if(PREFETCH_POLICY!=1 && PREFETCH_POLICY!=2) $fatal(1,"PREFETCH_POLICY must be 1 or 2");
 end
 // synthesis translate_on
 integer i;
 always @(posedge clk) begin
  if(rst) begin
   state<=IDLE; demand_pending<=0; cpu_rsp_valid<=0; cpu_rsp_data<=0;
   demand_addr<=0; tx_line<=0; tx_prefetch<=0; pf_pending<=0; pf_line<=0;
   stat_access<=0; stat_hit<=0; stat_miss<=0;
   stat_pf_issued<=0; stat_pf_useful<=0; stat_pf_unused<=0;
   for(i=0;i<N;i=i+1) begin valid[i]<=0; prefetched[i]<=0; tags[i]<=0; data[i]<=0; end
  end else begin
   if(cpu_rsp_valid && cpu_rsp_ready) cpu_rsp_valid<=0;
   if(!prefetch_enable) pf_pending<=0;
   else if(candidate_valid) begin pf_pending<=1; pf_line<=candidate_line; end
   if(accept) begin
    stat_access<=stat_access+1;
    if(hit) begin
     stat_hit<=stat_hit+1; cpu_rsp_valid<=1;
     cpu_rsp_data<=data[idx][cpu_req_addr[3:2]*32 +: 32];
     if(prefetched[idx]) begin stat_pf_useful<=stat_pf_useful+1; prefetched[idx]<=0; end
    end else begin
     stat_miss<=stat_miss+1; demand_pending<=1; demand_addr<=cpu_req_addr;
    end
   end
   case(state)
    IDLE: begin
     if(demand_pending) begin
      // Recheck: a prefetch may have satisfied this queued demand.
      if(valid[demand_addr[INDEX_BITS+3:4]] && tags[demand_addr[INDEX_BITS+3:4]]==demand_addr[31:4]) begin
       cpu_rsp_valid<=1;
       cpu_rsp_data<=data[demand_addr[INDEX_BITS+3:4]][demand_addr[3:2]*32 +:32];
       demand_pending<=0;
       // Late prefetch is not a hit or an on-time useful prefetch.
       prefetched[demand_addr[INDEX_BITS+3:4]]<=0;
      end else begin tx_line<=demand_addr[31:4]; tx_prefetch<=0; state<=SEND; end
     end else if(!accept && pf_pending && prefetch_enable) begin
      pf_pending<=0;
      if(!(valid[pf_idx] && tags[pf_idx]==pf_line)) begin
       tx_line<=pf_line; tx_prefetch<=1; state<=SEND;
      end
     end
    end
    SEND: if(mem_req_ready) begin
     state<=WAIT;
     if(tx_prefetch) stat_pf_issued<=stat_pf_issued+1;
    end
    WAIT: if(mem_rsp_valid) begin
     if(valid[tx_idx] && prefetched[tx_idx]) stat_pf_unused<=stat_pf_unused+1;
     data[tx_idx]<=mem_rsp_data; tags[tx_idx]<=tx_line; valid[tx_idx]<=1;
     prefetched[tx_idx]<=tx_prefetch;
     if(!tx_prefetch) begin
      cpu_rsp_valid<=1; cpu_rsp_data<=mem_rsp_data[demand_addr[3:2]*32 +:32];
      demand_pending<=0;
     end
     state<=IDLE;
    end
    default: state<=IDLE;
   endcase
  end
 end
endmodule
