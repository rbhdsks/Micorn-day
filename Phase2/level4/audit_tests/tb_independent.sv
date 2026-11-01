`timescale 1ns/1ps
`default_nettype none
// Independently written memory/driver/scoreboard. Does not use dram_model.sv.
module tb_independent;
 parameter REGION_ENABLE=1, FEEDBACK_ENABLE=1, VICTIM_ENABLE=0;
 parameter SEED=32'h93abc217, REQUESTS=4000;
 reg clk=0; always #5 clk=~clk;
 reg rst=1,en=1,cv=0,cr=0,mq=0,sv=0;
 reg[31:0]ca=0;reg[127:0]sd=0;
 wire cq,rv,mv,sq;wire[31:0]rd,ma;
 wire[31:0]a,h,m,pi,pu,pw,bh,late,suppressed;
 ai_cache_context #(.INDEX_BITS(3),.REGION_ENABLE(REGION_ENABLE),
  .FEEDBACK_ENABLE(FEEDBACK_ENABLE),.VICTIM_ENABLE(VICTIM_ENABLE)) dut(
  clk,rst,en,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,a,h,m,pi,pu,pw,bh,late,suppressed);
 reg[31:0]random_state=SEED,memory_line=0,expected_word=0;
 reg memory_busy=0,outstanding=0,held_request=0,held_response=0,held_input=0;
 reg[31:0]saved_ma=0,saved_rd=0,saved_ca=0;
 integer delay_left=0,accepted_total=0,checked=0,canceled=0,epoch_requests=0;
 integer cycles=0,resets_send=0,resets_wait=0,epoch=0,j,resident;
 integer visits[0:2],edges[0:8];
 reg prev_valid=0;reg[1:0]prev_state=0;reg prev_ready=0,prev_response=0;
 function automatic[31:0]step(input[31:0]x);
  reg[31:0]z;begin z=x^(x<<13);z=z^(z>>17);step=z^(z<<5);end
 endfunction
 function automatic[31:0]address(input integer n,input[31:0]r);
  case((n/80)%6)
   0:address=32'h1000+((32'(n)%128)<<4); // regular stream
   1:address=32'h8000+((r%128)<<2); // irregular word reads
   2:address=(n%2!=0 ? 32'h2000:32'h6000)+((32'(n/2)%96)<<4); // two regions
   3:address=32'h3000+((32'(n)%5)<<7); // same-index conflict
   4:address=32'hffffffe0-((32'(n)%48)<<4); // negative strides at upper bound
   default:address=32'h9000+((r%4)<<2); // hot line and word offsets
  endcase
 endfunction
 // Memory responses hold until consumed. The latency/ready sequence depends
 // only on this test's PRNG and not on the original benchmark memory model.
 always @(posedge clk) begin
  if(rst)begin memory_busy<=0;sv<=0;delay_left<=0;sd<=0;end
  else begin
   if(sv&&sq)begin sv<=0;memory_busy<=0;end
   if(mv&&mq)begin
    if(memory_busy || sv)$fatal(1,"independent memory accepted two requests");
    memory_line<=ma;memory_busy<=1;delay_left<=1+int'(random_state[7:3]);
   end
   if(memory_busy&&!sv)begin
    if(delay_left>0)delay_left<=delay_left-1;
    else begin
     for(integer w=0;w<4;w=w+1)sd[w*32+:32]<=((memory_line>>2)+32'(w))^32'hcafe1234;
     sv<=1;
    end
   end
  end
 end
 always @(posedge clk)begin
  cycles=cycles+1;
  if(rst)begin
   if(outstanding)canceled=canceled+1;
   outstanding=0;held_request=0;held_response=0;held_input=0;prev_valid=0;epoch_requests=0;
   if(cq || mv || sq)$fatal(1,"reset transfer masking");
  end else begin
   if(dut.state>2)$fatal(1,"unknown/illegal state");
   visits[dut.state]=visits[dut.state]+1;
   if(prev_valid)begin
    edges[prev_state*3+dut.state]=edges[prev_state*3+dut.state]+1;
    if(prev_state==1 && dut.state!=(prev_ready?2:1))$fatal(1,"SEND transition");
    if(prev_state==2 && dut.state!=(prev_response?0:2))$fatal(1,"WAIT transition");
    if(prev_state==0 && dut.state==2)$fatal(1,"IDLE skipped SEND");
   end
   if(held_request&&(!mv || ma!==saved_ma))$fatal(1,"request changed while blocked");
   if(held_response&&(!rv || rd!==saved_rd))$fatal(1,"response changed while blocked");
   if(held_input&&(!cv || ca!==saved_ca))$fatal(1,"independent source changed blocked request");
   held_request=mv&&!mq;saved_ma=ma;held_response=rv&&!cr;saved_rd=rd;
   held_input=cv&&!cq;saved_ca=ca;
   if(rv&&cr)begin
    if(!outstanding || rd!==expected_word)$fatal(1,"independent scoreboard data/order failure");
    checked=checked+1;outstanding=0;
   end
   if(cv&&cq)begin
    if(outstanding)$fatal(1,"CPU outstanding greater than one");
    if(ca[1:0]!=0)$fatal(1,"unaligned test demand");
    expected_word=(ca>>2)^32'hcafe1234;outstanding=1;
    accepted_total=accepted_total+1;epoch_requests=epoch_requests+1;
   end
   if(dut.buffer_valid[0]&&dut.buffer_valid[1]&&dut.buffer_line[0]==dut.buffer_line[1])$fatal(1,"duplicate buffer lines");
   for(j=0;j<2;j=j+1)
    if(dut.buffer_valid[j]&&dut.valid[dut.buffer_line[j][2:0]]&&
      dut.tags[dut.buffer_line[j][2:0]]==dut.buffer_line[j])$fatal(1,"duplicate cache/buffer line");
   prev_valid=1;prev_state=dut.state;prev_ready=mq;prev_response=sv;
  end
  if(cycles>1500000)$fatal(1,"independent progress watchdog");
 end
 // One edge later driver observes the handshakes from the preceding rising edge.
 reg sent_last=0;
 always @(negedge clk)begin
  random_state=step(random_state);
  if(rst)begin cv=0;cr=0;mq=0;sent_last=0;end
  else begin
   cr=(random_state[2:0]!=0);mq=(!memory_busy&&!sv&&random_state[4:3]!=0);
   // Hold valid/address until the immediately preceding acceptance is observed.
   if(sent_last)cv=0;
   if(!cv && accepted_total<REQUESTS && random_state[6:5]!=0)begin
    ca=address(accepted_total,random_state);cv=1;
   end
   en=(accepted_total%97<83);
  end
 end
 always @(posedge clk)sent_last<=!rst&&cv&&cq;
 task reset_epoch;
  begin @(negedge clk);rst=1;epoch=epoch+1;repeat(3)@(negedge clk);rst=0;end
 endtask
 initial begin
  for(j=0;j<3;j=j+1)visits[j]=0;for(j=0;j<9;j=j+1)edges[j]=0;
  repeat(4)@(negedge clk);rst=0;
  // Reset both endpoints while a request is selected, and then during response wait.
  wait(accepted_total>=200);wait(dut.state==1&&!mq);resets_send=1;reset_epoch();
  wait(accepted_total>=450);wait(dut.state==2);resets_wait=1;reset_epoch();
  wait(accepted_total>=REQUESTS);wait(!outstanding);
  @(negedge clk);cv=0;en=0;cr=1;
  repeat(150)@(negedge clk);
  if(dut.state!=0 || dut.demand_pending || memory_busy || sv || rv)$fatal(1,"independent drain incomplete");
  resident=int'(dut.buffer_valid[0])+int'(dut.buffer_valid[1]);
  if(!VICTIM_ENABLE && pi!=pu+late+pw+32'(resident))$fatal(1,"independent fate conservation");
  if(VICTIM_ENABLE && (pi!=0||pu!=0||pw!=0||late!=0))$fatal(1,"victim issued speculation");
  if(accepted_total!=checked+canceled)$fatal(1,"reset epoch request conservation");
  if(!visits[0]||!visits[1]||!visits[2]||!edges[1]||!edges[4]||!edges[5]||!edges[6]||!edges[8])$fatal(1,"FSM coverage missing");
  $display("PASS: independent requests=%0d checked=%0d canceled=%0d SENDreset=%0d WAITreset=%0d cycles=%0d",accepted_total,checked,canceled,resets_send,resets_wait,cycles);
  $display("COVER: IDLE=%0d SEND=%0d WAIT=%0d edges=%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",visits[0],visits[1],visits[2],edges[0],edges[1],edges[2],edges[3],edges[4],edges[5],edges[6],edges[7],edges[8]);
  $finish;
 end
 integer telemetry=0;reg[1023:0]telemetry_path;
 initial begin
  if($value$plusargs("TELEMETRY=%s",telemetry_path))begin
   telemetry=$fopen(telemetry_path,"w");if(!telemetry)$fatal(1,"telemetry open failed");
   $fdisplay(telemetry,"cycle,state,cpu_valid,cpu_ready,rsp_valid,rsp_ready,mem_valid,mem_ready,mem_rsp_valid,mem_rsp_ready,reset,quality,prefetches,suppressed");
  end
 end
 always @(negedge clk)if(telemetry!=0&&cycles<250)
  $fdisplay(telemetry,"%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",cycles,dut.state,cv,cq,rv,cr,mv,mq,sv,sq,rst,dut.feedback_quality,pi,suppressed);
endmodule
`default_nettype wire
