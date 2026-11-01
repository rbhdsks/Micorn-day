`timescale 1ns/1ps
`default_nettype none
// Read-only Phase2 cache. Speculative fills are isolated in a two-line buffer.
// Main-cache hits and timely buffer consumption remain distinct statistics.
module ai_cache_context #(
 parameter INDEX_BITS=6, parameter REGION_ENABLE=1, parameter FEEDBACK_ENABLE=1,
 parameter REGION_ENTRIES=4, parameter REGION_LINE_BITS=8, parameter PROBE_INTERVAL=16,
 parameter VICTIM_ENABLE=0
)(
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
 output reg [31:0] stat_pf_issued, stat_pf_useful, stat_pf_unused,
 output reg [31:0] stat_buffer_hit, stat_pf_late, stat_pf_suppressed
);
 localparam N=1<<INDEX_BITS;
 typedef enum logic[1:0] {IDLE=2'd0,SEND=2'd1,WAIT=2'd2} state_t;
 localparam COOL_BITS=PROBE_INTERVAL>1 ? $clog2(PROBE_INTERVAL) : 1;
 localparam [COOL_BITS-1:0] LAST_PROBE=COOL_BITS'(PROBE_INTERVAL-1);
 state_t state;
 reg [127:0] data[0:N-1];
 reg [27:0] tags[0:N-1];
 reg valid[0:N-1];
 reg [127:0] buffer_data[0:1];
 reg [27:0] buffer_line[0:1];
 reg buffer_valid[0:1];
 reg buffer_replace;
 reg [1:0] feedback_quality;
 reg [COOL_BITS-1:0] probe_age;
 reg demand_pending;
 // Requests are word aligned. Store only the bits that affect data selection.
 reg [31:2] demand_addr;
 reg tx_prefetch;
 reg [27:0] tx_line;
 reg pf_pending;
 reg [27:0] pf_line;
 wire [27:0] req_line=cpu_req_addr[31:4];
 wire [INDEX_BITS-1:0] idx=req_line[INDEX_BITS-1:0];
 wire hit=valid[idx] && tags[idx]==req_line;
 wire req_b0=buffer_valid[0] && buffer_line[0]==req_line;
 wire req_b1=buffer_valid[1] && buffer_line[1]==req_line;
 wire req_buffer_hit=req_b0 || req_b1;
 wire req_slot=!req_b0;
 wire [INDEX_BITS-1:0] demand_idx=demand_addr[INDEX_BITS+3:4];
 wire demand_hit=valid[demand_idx] && tags[demand_idx]==demand_addr[31:4];
 wire demand_b0=buffer_valid[0] && buffer_line[0]==demand_addr[31:4];
 wire demand_b1=buffer_valid[1] && buffer_line[1]==demand_addr[31:4];
 wire demand_buffer_hit=demand_b0 || demand_b1;
 wire demand_slot=!demand_b0;
 wire [INDEX_BITS-1:0] tx_idx=tx_line[INDEX_BITS-1:0];
 wire [INDEX_BITS-1:0] pf_idx=pf_line[INDEX_BITS-1:0];
 wire pf_cached=valid[pf_idx] && tags[pf_idx]==pf_line;
 wire pf_buffered=(buffer_valid[0] && buffer_line[0]==pf_line) ||
                  (buffer_valid[1] && buffer_line[1]==pf_line);
 wire fill_slot=!buffer_valid[0] ? 1'b0 : (!buffer_valid[1] ? 1'b1 : buffer_replace);
 wire effective_enable=prefetch_enable && (VICTIM_ENABLE == 0);
 wire feedback_allow=(FEEDBACK_ENABLE == 0) || feedback_quality!=0 || probe_age==LAST_PROBE;
 wire candidate_valid;
 wire [27:0] candidate_line;
 wire accept=cpu_req_valid && cpu_req_ready;
 wire timely_event=accept && !hit && req_buffer_hit && (VICTIM_ENABLE == 0);
 wire late_event=state==IDLE && demand_pending && !demand_hit && demand_buffer_hit && (VICTIM_ENABLE == 0);
 wire waste_event=state==WAIT && mem_rsp_valid && tx_prefetch && buffer_valid[fill_slot];
 assign cpu_req_ready=!rst && !demand_pending && (!cpu_rsp_valid || cpu_rsp_ready)
                       && !(state==WAIT && mem_rsp_valid);
 assign mem_req_valid=!rst && state==SEND;
 assign mem_req_addr={tx_line,4'b0};
 assign mem_rsp_ready=!rst && state==WAIT;
 generate
  if(REGION_ENABLE != 0) begin:g_region
   region_stride_prefetcher #(.ENTRIES(REGION_ENTRIES),.REGION_LINE_BITS(REGION_LINE_BITS))
    predictor(clk,rst,effective_enable,accept,req_line,candidate_valid,candidate_line);
  end else begin:g_global
   stride_prefetcher predictor(clk,rst,effective_enable,accept,req_line,candidate_valid,candidate_line);
  end
 endgenerate
 // synthesis translate_off
 initial begin
  if(INDEX_BITS<1 || INDEX_BITS>27 || PROBE_INTERVAL<1)
   $fatal(1,"invalid cache-context configuration");
 end
 // synthesis translate_on
 integer i;
 always_ff @(posedge clk) begin
  if(rst) begin
   state<=IDLE;demand_pending<=0;demand_addr<=0;cpu_rsp_valid<=0;cpu_rsp_data<=0;
   tx_prefetch<=0;tx_line<=0;pf_pending<=0;pf_line<=0;buffer_replace<=0;
   feedback_quality<=2;probe_age<=0;
   stat_access<=0;stat_hit<=0;stat_miss<=0;stat_pf_issued<=0;
   stat_pf_useful<=0;stat_pf_unused<=0;stat_buffer_hit<=0;stat_pf_late<=0;stat_pf_suppressed<=0;
   // Only validity resets. Invalid payload/identity bits are never observed.
   // This avoids a reset network on the complete data array.
   for(i=0;i<N;i=i+1) valid[i]<=0;
   for(i=0;i<2;i=i+1) buffer_valid[i]<=0;
  end else begin
   if(cpu_rsp_valid && cpu_rsp_ready) cpu_rsp_valid<=0;
   // Training continues through runtime disable; only new speculation stops.
   if(accept && probe_age<LAST_PROBE) probe_age<=probe_age+1'b1;
   if(state==SEND && mem_req_ready && tx_prefetch) probe_age<=0;
   if(timely_event || late_event) begin
    if(feedback_quality!=3) feedback_quality<=feedback_quality+1'b1;
   end else if(waste_event && feedback_quality!=0) feedback_quality<=feedback_quality-1'b1;
   if(!effective_enable) pf_pending<=0;
   else if(candidate_valid) begin pf_pending<=1;pf_line<=candidate_line;end
   if(accept) begin
    stat_access<=stat_access+1;
    if(hit) begin
     stat_hit<=stat_hit+1;cpu_rsp_valid<=1;
     cpu_rsp_data<=data[idx][cpu_req_addr[3:2]*32 +:32];
    end else begin
     stat_miss<=stat_miss+1;
     if(req_buffer_hit) begin
      // Only a real demand promotes speculative data into the demand cache.
      data[idx]<=buffer_data[req_slot];tags[idx]<=req_line;valid[idx]<=1;
      if((VICTIM_ENABLE != 0) && valid[idx]) begin
       // Demand-only control: swap the evicted main-cache line into this slot.
       buffer_data[req_slot]<=data[idx];buffer_line[req_slot]<=tags[idx];buffer_valid[req_slot]<=1;
      end else buffer_valid[req_slot]<=0;
      stat_buffer_hit<=stat_buffer_hit+1;
      if((VICTIM_ENABLE == 0)) stat_pf_useful<=stat_pf_useful+1;
      cpu_rsp_valid<=1;
      cpu_rsp_data<=buffer_data[req_slot][cpu_req_addr[3:2]*32 +:32];
     end else begin demand_pending<=1;demand_addr<=cpu_req_addr[31:2];end
    end
   end
   case(state)
    IDLE:begin
     if(demand_pending) begin
      if(demand_hit) begin
       cpu_rsp_valid<=1;cpu_rsp_data<=data[demand_idx][demand_addr[3:2]*32 +:32];demand_pending<=0;
      end else if(demand_buffer_hit) begin
       data[demand_idx]<=buffer_data[demand_slot];tags[demand_idx]<=demand_addr[31:4];valid[demand_idx]<=1;
       cpu_rsp_valid<=1;cpu_rsp_data<=buffer_data[demand_slot][demand_addr[3:2]*32 +:32];
       if((VICTIM_ENABLE != 0) && valid[demand_idx]) begin
        buffer_data[demand_slot]<=data[demand_idx];buffer_line[demand_slot]<=tags[demand_idx];buffer_valid[demand_slot]<=1;
       end else buffer_valid[demand_slot]<=0;
       demand_pending<=0;if((VICTIM_ENABLE == 0)) stat_pf_late<=stat_pf_late+1;
      end else begin tx_line<=demand_addr[31:4];tx_prefetch<=0;state<=SEND;end
     end else if(!accept && pf_pending && effective_enable) begin
      pf_pending<=0;
      if(!pf_cached && !pf_buffered) begin
       if(feedback_allow) begin tx_line<=pf_line;tx_prefetch<=1;state<=SEND;end
       else stat_pf_suppressed<=stat_pf_suppressed+1;
      end
     end
    end
    SEND:if(mem_req_ready) begin
     state<=WAIT;if(tx_prefetch) stat_pf_issued<=stat_pf_issued+1;
    end
    WAIT:if(mem_rsp_valid) begin
     if(tx_prefetch) begin
      if(buffer_valid[fill_slot]) stat_pf_unused<=stat_pf_unused+1;
      buffer_data[fill_slot]<=mem_rsp_data;buffer_line[fill_slot]<=tx_line;buffer_valid[fill_slot]<=1;
      buffer_replace<=!fill_slot;
     end else begin
      if((VICTIM_ENABLE != 0) && valid[tx_idx]) begin
       buffer_data[fill_slot]<=data[tx_idx];buffer_line[fill_slot]<=tags[tx_idx];buffer_valid[fill_slot]<=1;
       buffer_replace<=!fill_slot;
      end
      data[tx_idx]<=mem_rsp_data;tags[tx_idx]<=tx_line;valid[tx_idx]<=1;
      cpu_rsp_valid<=1;cpu_rsp_data<=mem_rsp_data[demand_addr[3:2]*32 +:32];demand_pending<=0;
     end
     state<=IDLE;
    end
    default:state<=IDLE;
   endcase
  end
 end
endmodule

`default_nettype wire
