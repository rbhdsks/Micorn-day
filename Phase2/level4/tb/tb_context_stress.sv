`timescale 1ns/1ps
`default_nettype none
module tb_context_stress;
 parameter REGION_ENABLE=1;
 parameter FEEDBACK_ENABLE=1;
 parameter VICTIM_ENABLE=0;
 parameter SEED=32'h4d2d3f97;
 reg clk=0; always #5 clk=~clk;
 reg rst=1, enable=1, cv=0, cr=0;
 reg [31:0] ca=0, rng=SEED;
 wire cq,rv,mv,mq,sv,sq;
 wire [31:0] rd,ma,accesses,hits,misses,issued,useful,unused,reads,bh,late,suppressed;
 wire [127:0] sd;
 ai_cache_context #(.REGION_ENABLE(REGION_ENABLE),.FEEDBACK_ENABLE(FEEDBACK_ENABLE),.VICTIM_ENABLE(VICTIM_ENABLE)) dut(clk,rst,enable,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,accesses,hits,misses,issued,useful,unused,bh,late,suppressed);
 dram_model #(.LATENCY(3)) dram(clk,rst,mv,mq,ma,sv,sq,sd,reads);
 context_protocol_monitor monitor(clk,rst,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,dut.state,dut.demand_pending);
 integer invariant_j;
 always @(posedge clk) if(!rst) begin
  if(dut.buffer_valid[0] && dut.buffer_valid[1] && dut.buffer_line[0]==dut.buffer_line[1])$fatal(1,"duplicate buffer lines");
  for(invariant_j=0;invariant_j<2;invariant_j=invariant_j+1)
   if(dut.buffer_valid[invariant_j] && dut.valid[dut.buffer_line[invariant_j][5:0]] &&
      dut.tags[dut.buffer_line[invariant_j][5:0]]==dut.buffer_line[invariant_j])$fatal(1,"cache/buffer duplicate");
 end
 reg [31:0] expected[0:1999];
 integer sent=0,received=0,ticks=0;
 reg prev_blocked=0, accepted=0;
 reg [31:0] held;
 initial begin repeat(4) @(negedge clk); rst=0; end
 always @(negedge clk) if(!rst) begin
  rng=rng^(rng<<13);rng=rng^(rng>>17);rng=rng^(rng<<5);
  cr=(rng[3:0]>4); // Arbitrary consumer stalls, independent of request timing.
  enable=(ticks%211<170);
  if(!cv || accepted) begin
   cv=(sent<2000);
   case((sent/100)%4)
    0: ca=32'h1000+(sent%64)*4;
    1: ca=32'h4000+sent*16;
    2: ca=32'h2000+(rng%2048)*4;
    3: ca=32'h8000-(sent%100)*64;
   endcase
  end
 end
 always @(posedge clk) if(!rst) begin
  ticks=ticks+1;
  accepted=cv && cq;
  if(prev_blocked && (!rv || rd!==held)) $fatal(1,"stress: response unstable");
  prev_blocked=rv && !cr; held=rd;
  if(cv && cq) begin
   if(sent>=2000) $fatal(1,"excess request");
   expected[sent]=(ca>>2)^32'hcafe1234; sent=sent+1;
  end
  if(rv && cr) begin
   if(received>=sent || rd!==expected[received]) $fatal(1,"stress: lost/reordered/wrong response %0d",received);
   received=received+1;
  end
  if(received==2000) begin
   if(accesses!=2000 || hits+misses!=accesses) $fatal(1,"stress counters");
   $display("PASS: continuous-request stress, 2000 ordered responses, %0d cycles",ticks); $finish;
  end
  if(ticks>100000) $fatal(1,"stress timeout");
 end
endmodule

`default_nettype wire
