`timescale 1ns/1ps
`default_nettype none
module tb_context_nonpreemptible;
 parameter REGION_ENABLE=1;
 parameter FEEDBACK_ENABLE=1;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,en=1,cv=0,cr=1,mq=0,sv=0;
 reg[31:0]ca=0;reg[127:0]sd=0;
 wire cq,rv,mv,sq;wire[31:0]rd,ma,a,h,m,pi,pu,pw,bh,late,suppressed;
 ai_cache_context #(.REGION_ENABLE(REGION_ENABLE),.FEEDBACK_ENABLE(FEEDBACK_ENABLE)) dut(clk,rst,en,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,a,h,m,pi,pu,pw,bh,late,suppressed);
 integer j,k;
 task demand(input[31:0] addr);
 begin
  @(negedge clk);ca=addr;cv=1;
  do @(posedge clk);while(!cq);
  @(negedge clk);cv=0;
  // Manually service demand memory request immediately upon its presentation.
  wait(mv);@(negedge clk);mq=1;
  @(negedge clk);mq=0;
  for(j=0;j<4;j=j+1)sd[j*32+:32]=((addr+4*j)>>2)^32'hcafe1234;
  sv=1;
  @(negedge clk);sv=0;
  wait(rv);if(rd!==((addr>>2)^32'hcafe1234))$fatal(1,"training response data mismatch");@(negedge clk);
 end endtask
 initial begin
  repeat(4)@(negedge clk);rst=0;
  demand(32'h1000);demand(32'h1010);demand(32'h1020);
  wait(mv); // Prefetch 0x1030 is now selected; ready remains zero.
  if(ma!==32'h1030 || !dut.tx_prefetch)$fatal(1,"unexpected transaction");
  @(negedge clk);ca=32'h8000;cv=1;
  do @(posedge clk);while(!cq);
  @(negedge clk);cv=0;
  for(k=0;k<20;k=k+1)begin
   @(negedge clk);
   if(!mv || ma!==32'h1030 || !dut.demand_pending || rv)$fatal(1,"unexpected preemption");
  end
  $display("PASS: limitation demonstration: unrelated demand accepted but held for 20 cycles behind unaccepted prefetch 0x1030 in SEND.");
  $finish;
 end
 initial begin #100000;$fatal(1,"timeout");end
endmodule

`default_nettype wire
