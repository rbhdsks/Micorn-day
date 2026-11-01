`timescale 1ns/1ps
`default_nettype none
// Forced candidate pulses isolate controller decisions from predictor training.
// All requests/fills still traverse real ready/valid and data storage logic.
module tb_context_directed;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,en=0,cv=0,cr=0;
 reg[31:0]ca=0;reg[27:0]inject_line=0;
 wire cq,rv,mv,mq,sv,sq;wire[31:0]rd,ma;
 wire[127:0]sd;wire[31:0]a,h,m,pi,pu,pw,bh,late,suppressed,reads;
 ai_cache_context #(.INDEX_BITS(2)) dut(clk,rst,en,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,a,h,m,pi,pu,pw,bh,late,suppressed);
 dram_model #(.LATENCY(6)) dram(clk,rst,mv,mq,ma,sv,sq,sd,reads);
 context_protocol_monitor monitor(clk,rst,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,dut.state,dut.demand_pending);
 integer checked=0,k,previous_reads;reg[31:0]held;
 task quiet;
 integer count,watchdog;
 begin
  count=0;watchdog=0;
  while(count<3) begin
   @(negedge clk);watchdog=watchdog+1;
   if(dut.state==0 && !dut.demand_pending && !dut.pf_pending && !dut.candidate_valid && !rv && !mv && !sv)count=count+1;else count=0;
   if(watchdog>1000)$fatal(1,"quiet timeout");
  end
 end endtask
 task pulse(input[27:0] line);
 begin
  @(negedge clk);inject_line=line;
  force dut.candidate_valid=1'b1;force dut.candidate_line=inject_line;
  @(negedge clk);release dut.candidate_valid;release dut.candidate_line;
 end endtask
 task read_word(input[31:0]addr,input integer stall);
 integer watchdog;
 begin
  @(negedge clk);ca=addr;cv=1;cr=0;watchdog=0;
  do begin @(posedge clk);watchdog=watchdog+1;if(watchdog>2000)$fatal(1,"accept timeout");end while(!cq);
  @(negedge clk);cv=0;
  while(!rv)begin @(negedge clk);watchdog=watchdog+1;if(watchdog>2000)$fatal(1,"response timeout");end
  if(rd!==((addr>>2)^32'hcafe1234))$fatal(1,"directed bad data %h",addr);
  held=rd;
  repeat(stall)begin @(negedge clk);if(!rv || rd!==held)$fatal(1,"directed stalled response changed");end
  cr=1;@(negedge clk);cr=0;checked=checked+1;
 end endtask
 task reset_all;
 begin
  @(negedge clk);rst=1;cv=0;cr=0;repeat(3)@(negedge clk);rst=0;
  if(rv || mv || sv || a || pi || bh || late || pw || dut.buffer_valid[0] || dut.buffer_valid[1])$fatal(1,"shared reset failed");
 end endtask
 initial begin
  repeat(4)@(negedge clk);rst=0;
  read_word('h1000,3);quiet();en=1;
  pulse('h104);quiet(); // maps to same cache index as hot 0x1000
  if(!dut.valid[0] || dut.tags[0]!='h100)$fatal(1,"speculative fill polluted demand cache");
  previous_reads=reads;read_word('h1000,2);quiet();if(reads!=previous_reads)$fatal(1,"hot line lost");
  pulse('h104);quiet();if(reads!=previous_reads)$fatal(1,"duplicate buffer candidate fetched");
  read_word('h104c,4);quiet();if(bh!=1 || pu!=1)$fatal(1,"buffer hit was not counted separately");
  previous_reads=reads;pulse('h104);quiet();if(reads!=previous_reads)$fatal(1,"duplicate cached candidate fetched");
  pulse('h105);quiet();pulse('h106);quiet();pulse('h107);quiet();
  if(pw!=1)$fatal(1,"buffer replacement waste count");
  // Two initial-quality waste events close gate; residents remain unresolved.
  pulse('h108);quiet();if(dut.feedback_quality!=1)$fatal(1,"mature feedback decrement");
  pulse('h109);quiet();if(dut.feedback_quality!=0)$fatal(1,"feedback did not saturate to zero");
  previous_reads=reads;pulse('h10a);quiet();if(reads!=previous_reads || suppressed==0)$fatal(1,"gate failed to suppress");
  // Sixteen real accepted demands age a recovery probe even with no new predictions.
  for(k=0;k<16;k=k+1)read_word('h1000,0);
  quiet();pulse('h10a);quiet();if(reads!=previous_reads+2)$fatal(1,"bounded probe not issued");
  // previous_reads includes buffer work before 16 requests; first hot read refills once.
  read_word('h10a4,2);quiet();if(dut.feedback_quality!=1)$fatal(1,"useful probe did not reopen quality gate");
  // Disabled selection does not discard existing buffer data.
  pulse('h10b);quiet();en=0;read_word('h10b0,2);quiet();
  previous_reads=reads;pulse('h10c);quiet();if(reads!=previous_reads)$fatal(1,"disable allowed new selection");
  // Reset while SEND is unaccepted: no stale request may survive shared reset.
  en=1;pulse('h180);wait(dut.state==1);reset_all();quiet();
  // Reset while memory is active drops both shared endpoints and all metadata.
  en=1;pulse('h200);wait(dut.state==2);reset_all();quiet();
  if(reads!=0)$fatal(1,"memory reset mismatch");
  read_word('h2000,1);quiet();
  // A demand for the selected speculative line is late, rechecks, no duplicate read.
  reset_all();en=1;pulse('h300);wait(dut.state==2);read_word('h3008,3);quiet();
  if(late!=1 || bh!=0 || reads!=1 || pi!=1)$fatal(1,"late fill duplicated or misclassified");
  $display("PASS: context directed %0d checked demand responses, pollution/filter/replacement/gate/probe/disable/reset/late paths",checked);$finish;
 end
 initial begin #1000000;$fatal(1,"directed watchdog");end
endmodule

`default_nettype wire
