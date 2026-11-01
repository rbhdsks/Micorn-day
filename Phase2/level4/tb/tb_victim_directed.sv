`timescale 1ns/1ps
`default_nettype none
module tb_victim_directed;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,en=1,cv=0,cr=0;reg[31:0]ca=0;
 wire cq,rv,mv,mq,sv,sq;wire[31:0]rd,ma;
 wire[127:0]sd;wire[31:0]a,h,m,pi,pu,pw,bh,late,suppressed,reads;
 ai_cache_context #(.INDEX_BITS(2),.VICTIM_ENABLE(1)) dut(clk,rst,en,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,a,h,m,pi,pu,pw,bh,late,suppressed);
 dram_model #(.LATENCY(5)) dram(clk,rst,mv,mq,ma,sv,sq,sd,reads);
 context_protocol_monitor monitor(clk,rst,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,dut.state,dut.demand_pending);
 integer checked=0,k;reg[31:0]held;
 task read_word(input[31:0]addr);
 integer watchdog;
 begin
  @(negedge clk);ca=addr;cv=1;cr=0;watchdog=0;
  do begin @(posedge clk);watchdog=watchdog+1;if(watchdog>1000)$fatal(1,"victim accept timeout");end while(!cq);
  @(negedge clk);cv=0;
  while(!rv)begin @(negedge clk);watchdog=watchdog+1;if(watchdog>1000)$fatal(1,"victim response timeout");end
  if(rd!==((addr>>2)^32'hcafe1234))$fatal(1,"victim bad data %h",addr);
  held=rd;repeat(checked%4)begin @(negedge clk);if(!rv || rd!==held)$fatal(1,"victim stalled response");end
  cr=1;@(negedge clk);cr=0;checked=checked+1;
 end endtask
 initial begin
  repeat(4)@(negedge clk);rst=0;
  for(k=0;k<3;k=k+1)begin read_word('h1000);read_word('h1040);read_word('h1080);end
  if(reads!=3 || bh!=6 || pi || pu || late || pw)$fatal(1,"victim equal-data control failed");
  read_word('h10c0);read_word('h1000);
  if(reads!=5)$fatal(1,"victim capacity/replacement failed");
  read_word('h100c);if(h!=1)$fatal(1,"victim word-offset main-cache hit failed");
  @(negedge clk);rst=1;repeat(3)@(negedge clk);rst=0;
  if(dut.buffer_valid[0] || dut.buffer_valid[1] || rv || pi || bh)$fatal(1,"victim reset failed");
  read_word('h1044);if(reads!=1)$fatal(1,"victim reset retained data");
  $display("PASS: victim directed %0d checked responses, demand eviction/swap/capacity/offset/reset",checked);$finish;
 end
 initial begin #1000000;$fatal(1,"victim watchdog");end
endmodule

`default_nettype wire
