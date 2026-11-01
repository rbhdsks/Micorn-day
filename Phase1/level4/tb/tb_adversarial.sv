`timescale 1ns/1ps
module tb_adversarial;
 reg clk=0; always #5 clk=~clk;
 reg rst=1,enable=1,cv=0,cr=0,mq=0,sv=0;
 reg[31:0]ca=0; reg[127:0]sd=0;
 wire cq,rv,mv,sq; wire[31:0]rd,ma,accesses,hits,misses,issued,useful,unused;
 ai_cache #(.INDEX_BITS(2)) dut(clk,rst,enable,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,accesses,hits,misses,issued,useful,unused);
 reg[31:0]rng=32'h4d2d3f97, expected[0:49999], memaddr=0;
 integer sent=0,received=0,ticks=0,delay_left=0,epoch=0,reads=0;
 reg accepted=0,mbusy=0,prev_blocked=0,prev_req_blocked=0; reg[31:0]held=0,heldma=0;
 integer j;
 initial begin repeat(4) @(negedge clk);rst=0;end
 always @(negedge clk) if(!rst) begin
  rng=rng^(rng<<13); rng=rng^(rng>>17); rng=rng^(rng<<5);
  // Long blocked periods, continuously held requests, dynamically disabled predictor.
  cr=(ticks%127<65) && rng[0]; mq=!mbusy && !sv && (rng[7:4]>5);
  enable=(ticks%277<179);
  if(!cv || accepted) begin
   cv=(sent<10000);
   case((sent/17)%6)
    0:ca=32'h1000+(sent%4)*4;
    1:ca=32'h1000+sent*16;
    2:ca=32'h8000-(sent%100)*64;
    3:ca=32'h4000+(rng%256)*4;
    4:ca=32'hf0000000+((sent%2)*64);
    5:ca=(rng & 32'hfffffffc);
   endcase
  end
 end
 always @(posedge clk) if(!rst) begin
  ticks=ticks+1; accepted=cv&&cq;
  if(prev_blocked && (!rv || rd!==held)) $fatal(1,"response unstable");
  prev_blocked=rv&&!cr; held=rd;
  if(prev_req_blocked && (!mv || ma!==heldma)) $fatal(1,"memory request unstable");
  prev_req_blocked=mv&&!mq;heldma=ma;
  if(cv&&cq) begin expected[sent]=(ca>>2)^32'hcafe1234;sent=sent+1;end
  if(rv&&cr) begin
   if(received>=sent || rd!==expected[received]) $fatal(1,"bad response %0d",received);
   received=received+1;
  end
  if(sv&&sq) sv<=0;
  if(mv&&mq) begin
   if(mbusy || sv) $fatal(1,"overlapping memory request");
   memaddr<=ma;mbusy<=1;delay_left<=rng[12:8];reads=reads+1;
  end
  if(mbusy) begin
   if(delay_left==0) begin
    for(j=0;j<4;j=j+1) sd[j*32+:32]<=((memaddr+4*j)>>2)^32'hcafe1234;
    sv<=1;mbusy<=0;
   end else delay_left<=delay_left-1;
  end
  if(received==10000) begin
   if(accesses!=10000 || hits+misses!=accesses) $fatal(1,"counter mismatch");
   $display("PASS: adversarial: %0d responses, %0d cycles, %0d reads, hits=%0d misses=%0d PF=%0d",received,ticks,reads,hits,misses,issued);$finish;
  end
  if(ticks>3000000) $fatal(1,"watchdog");
 end
endmodule
