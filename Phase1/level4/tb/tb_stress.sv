`timescale 1ns/1ps
module tb_stress;
 reg clk=0; always #5 clk=~clk;
 reg rst=1, enable=1, cv=0, cr=0;
 reg [31:0] ca=0, rng=32'habcd1234;
 wire cq,rv,mv,mq,sv,sq;
 wire [31:0] rd,ma,accesses,hits,misses,issued,useful,unused,reads;
 wire [127:0] sd;
 ai_cache dut(clk,rst,enable,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,accesses,hits,misses,issued,useful,unused);
 dram_model #(.LATENCY(3)) dram(clk,rst,mv,mq,ma,sv,sq,sd,reads);
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
