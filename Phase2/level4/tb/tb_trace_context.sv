`timescale 1ns/1ps
`default_nettype none
// Serial trace replay. Gap is imposed only between demands, never after the last.
// Metrics distinguish demand completion from natural speculative drain.
module tb_trace_context;
 parameter INDEX_BITS=6;
 parameter LATENCY=12;
 parameter REGION_ENABLE=1;
 parameter FEEDBACK_ENABLE=1;
 parameter REGION_ENTRIES=4;
 parameter REGION_LINE_BITS=8;
 parameter PROBE_INTERVAL=16;
 parameter VICTIM_ENABLE=0;
 reg clk=0; always #5 clk=~clk;
 reg rst=1, enable=0;
 reg cv=0, cr=0;
 reg [31:0] ca=0;
 wire cq,rv,mv,mq,sv,sq;
 wire [31:0] rd,ma;
 wire [127:0] sd;
 wire [31:0] accesses,hits,misses,issued,useful,unused,reads,buffer_hits,late,suppressed;
 ai_cache_context #(.INDEX_BITS(INDEX_BITS),.REGION_ENABLE(REGION_ENABLE),.FEEDBACK_ENABLE(FEEDBACK_ENABLE),
  .REGION_ENTRIES(REGION_ENTRIES),.REGION_LINE_BITS(REGION_LINE_BITS),.PROBE_INTERVAL(PROBE_INTERVAL),.VICTIM_ENABLE(VICTIM_ENABLE)) dut(
  clk,rst,enable,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,
  accesses,hits,misses,issued,useful,unused,buffer_hits,late,suppressed);
 dram_model #(.LATENCY(LATENCY)) dram(clk,rst,mv,mq,ma,sv,sq,sd,reads);

 reg [63:0] cycles=0,start_cycle=0,completion_cycles=0,cycle_budget=0;
 reg [63:0] latency_sum=0,max_latency=0,offer_latency_sum=0,max_offer_latency=0;
 reg [63:0] request_wait_cycles=0,total_compute_gap_cycles=0;
 localparam [63:0] TRANSACTION_TIMEOUT=64'd1024+64'd4*LATENCY;
 integer checked=0,n,mode,k,fd,sample_fd=0,resident=0,j,quiet=0;
 reg [63:0] trace_rows[0:65535];
 string trace_file,output_file,sample_file;
 always @(posedge clk) begin
  cycles<=cycles+64'd1;
  if(!rst && cycle_budget!=0 && cycles-start_cycle>cycle_budget)
   $fatal(1,"input-derived trace watchdog");
 end
 // Every memory producer holds payload until a rising-edge transfer.
 reg blocked=0;
 reg [31:0] held_addr=0;
 always @(posedge clk) begin
  if(rst) blocked<=0;
  else begin
   if(blocked && (!mv || ma!==held_addr)) $fatal(1,"trace: unstable memory request");
   blocked<=mv && !mq; held_addr<=ma;
   if(mv && ma[3:0]!=0) $fatal(1,"trace: unaligned memory request");
  end
 end

 task automatic read_word(input [31:0] a,input integer stall,input integer gap);
  reg [63:0] watchdog,accepted_cycle,offered_cycle,response_latency,offer_latency;
  integer q;
  reg [31:0] expected,held;
  begin
   expected=(a>>2)^32'hcafe1234;
   @(negedge clk);ca=a;cv=1;cr=0;watchdog=0;offered_cycle=cycles;
   do begin
    @(posedge clk);watchdog=watchdog+1;
    if(watchdog>TRANSACTION_TIMEOUT) $fatal(1,"request timeout");
   end while(!cq);
   accepted_cycle=cycles;
   request_wait_cycles=request_wait_cycles+(accepted_cycle-offered_cycle);
   @(negedge clk);cv=0;watchdog=0;
   while(!rv) begin
    @(negedge clk);watchdog=watchdog+1;
    if(watchdog>TRANSACTION_TIMEOUT) $fatal(1,"response timeout");
   end
   if(rd!==expected) $fatal(1,"data mismatch a=%h expected=%h got=%h",a,expected,rd);
   response_latency=cycles-accepted_cycle;offer_latency=cycles-offered_cycle;
   latency_sum=latency_sum+response_latency;
   offer_latency_sum=offer_latency_sum+offer_latency;
   if(response_latency>max_latency) max_latency=response_latency;
   if(offer_latency>max_offer_latency) max_offer_latency=offer_latency;
   if(sample_fd) $fdisplay(sample_fd,"%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",checked,a,response_latency,offer_latency,accepted_cycle-offered_cycle,dut.feedback_quality,issued,suppressed);
   held=rd;
   for(q=0;q<stall;q=q+1) begin
    @(negedge clk);
    if(!rv || rd!==held) $fatal(1,"response changed under backpressure");
   end
   cr=1;
   @(negedge clk);cr=0;checked=checked+1;
   completion_cycles=cycles-start_cycle;
   total_compute_gap_cycles=total_compute_gap_cycles+gap;
   repeat(gap) @(negedge clk);
  end
 endtask

 initial begin
  if(!$value$plusargs("TRACE=%s",trace_file) || !$value$plusargs("COUNT=%d",n) ||
     !$value$plusargs("PF=%d",mode) || !$value$plusargs("OUT=%s",output_file))
   $fatal(1,"required: TRACE COUNT PF OUT");
  if(n<1 || n>65536 || (mode!=0 && mode!=1) || LATENCY<0) $fatal(1,"bad arguments");
  if($value$plusargs("SAMPLE_OUT=%s",sample_file)) begin
   sample_fd=$fopen(sample_file,"w");
   if(!sample_fd) $fatal(1,"cannot open sample CSV");
   $fdisplay(sample_fd,"request_index,address,accept_latency,offer_latency,request_wait,feedback_quality,cumulative_prefetch_issued,cumulative_suppressed");
  end
  $readmemh(trace_file,trace_rows,0,n-1);
  cycle_budget=64'd1024+n*TRANSACTION_TIMEOUT;
  for(k=0;k<n;k=k+1) begin
   if((^trace_rows[k])===1'bx) $fatal(1,"missing or unknown trace row");
   if(trace_rows[k][33:32]!=0) $fatal(1,"unaligned trace");
   if(trace_rows[k][31:0]>100000) $fatal(1,"gap outside supported 0..100000");
   if(k<n-1) cycle_budget=cycle_budget+trace_rows[k][31:0];
  end
  repeat(4) @(negedge clk);
  rst=0;enable=(mode!=0);start_cycle=cycles;
  for(k=0;k<n;k=k+1)
   read_word(trace_rows[k][63:32],k%4,k==n-1 ? 0 : trace_rows[k][31:0]);

  // Require two settled quiet edges: a registered predictor candidate may not
  // yet have entered pf_pending when the final demand completes.
  quiet=0;
  while(quiet<2) begin
   @(negedge clk);
   if(dut.state==0 && !dut.demand_pending && !dut.candidate_valid &&
      !dut.pf_pending && !cv && !rv && !mv && !sv) quiet=quiet+1;
   else quiet=0;
  end
  for(j=0;j<2;j=j+1)
   if(dut.buffer_valid[j] && !VICTIM_ENABLE) resident=resident+1;
  if(accesses!=n || hits+misses!=n) $fatal(1,"trace counters");
  if(issued!=useful+late+unused+resident) $fatal(1,"prefetch fate accounting");
  if(!VICTIM_ENABLE && useful!=buffer_hits) $fatal(1,"timely buffer counter mismatch");
  if(VICTIM_ENABLE && (issued!=0 || useful!=0 || late!=0 || unused!=0)) $fatal(1,"victim mode issued speculation");
  if(mode==0 && issued!=0) $fatal(1,"disabled prefetch issued traffic");
  fd=$fopen(output_file,"w");
  if(fd==0) $fatal(1,"cannot open output CSV");
  $fdisplay(fd,"prefetch,prefetch_policy,index_bits,memory_latency,accesses,hits,misses,prefetch_issued,timely_useful,late_useful,unused_evicted,resident_unconsumed,dram_reads,cycles,completion_cycles,quiescent_cycles,latency_sum,max_latency,offer_latency_sum,max_offer_latency,request_wait_cycles,total_compute_gap_cycles,buffer_hits,predictions_suppressed,feedback_quality");
  $fdisplay(fd,"%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",mode,1,INDEX_BITS,LATENCY,accesses,hits,misses,issued,useful,late,unused,resident,reads,completion_cycles,completion_cycles,cycles-start_cycle,latency_sum,max_latency,offer_latency_sum,max_offer_latency,request_wait_cycles,total_compute_gap_cycles,buffer_hits,suppressed,dut.feedback_quality);
  $fclose(fd);if(sample_fd) $fclose(sample_fd);
  $display("PASS: trace %s pf=%0d policy=%0d checked=%0d completion=%0d quiescent=%0d",trace_file,mode,1,checked,completion_cycles,cycles-start_cycle);
  $finish;
 end
endmodule

`default_nettype wire
