`timescale 1ns/1ps
`default_nettype none
// Independent bus/FSM conservation monitor; synthesis never includes this file.
module context_protocol_monitor(
 input wire clk,rst,
 input wire cv,cq,input wire[31:0]ca,
 input wire rv,cr,input wire[31:0]rd,
 input wire mv,mq,input wire[31:0]ma,
 input wire sv,sq,input wire[127:0]sd,
 input wire[1:0]state,
 input wire demand_pending
);
 integer accepted=0,returned=0,mem_accepted=0,mem_returned=0;
 integer state_visits[0:2];integer transitions[0:8];
 reg prev_valid=0,prev_rst=1;
 reg[1:0]prev_state=0;
 reg prev_mq=0,prev_sv=0;
 reg blocked_req=0,blocked_rsp=0,blocked_cpu=0,blocked_mem_rsp=0;
 reg[31:0]held_ma=0,held_rd=0,held_ca=0;
 reg[127:0]held_sd=0;
 integer i;
 initial begin for(i=0;i<3;i=i+1)state_visits[i]=0;for(i=0;i<9;i=i+1)transitions[i]=0;end
 always @(posedge clk) begin
  if(rst) begin
   accepted=0;returned=0;mem_accepted=0;mem_returned=0;
   blocked_req=0;blocked_rsp=0;blocked_cpu=0;blocked_mem_rsp=0;prev_valid=0;
   if(mv || sq || cq)$fatal(1,"reset must suppress transfer readiness/validity");
  end else begin
   if(state>2)$fatal(1,"illegal FSM encoding");
   state_visits[state]=state_visits[state]+1;
   if(prev_valid && !prev_rst) begin
    transitions[prev_state*3+state]=transitions[prev_state*3+state]+1;
    if(prev_state==1 && state!=(prev_mq ? 2 : 1))$fatal(1,"SEND transition without exact request handshake");
    if(prev_state==2 && state!=(prev_sv ? 0 : 2))$fatal(1,"WAIT transition without exact response handshake");
    if(prev_state==0 && state!=0 && state!=1)$fatal(1,"IDLE skipped SEND");
   end
   if(mv!==(state==1))$fatal(1,"memory valid not exactly SEND");
   if(sq!==(state==2))$fatal(1,"memory response ready not exactly WAIT");
   if(demand_pending && cq)$fatal(1,"accepted second pending demand");
   if(blocked_req && (!mv || ma!==held_ma))$fatal(1,"memory request payload unstable");
   if(blocked_rsp && (!rv || rd!==held_rd))$fatal(1,"CPU response payload unstable");
   if(blocked_cpu && (!cv || ca!==held_ca))$fatal(1,"test source broke CPU valid hold");
   if(blocked_mem_rsp && (!sv || sd!==held_sd))$fatal(1,"memory model broke response hold");
   blocked_req=mv&&!mq;held_ma=ma;blocked_rsp=rv&&!cr;held_rd=rd;
   blocked_cpu=cv&&!cq;held_ca=ca;blocked_mem_rsp=sv&&!sq;held_sd=sd;
   if(cv&&cq) accepted=accepted+1;
   if(rv&&cr) returned=returned+1;
   if(mv&&mq) mem_accepted=mem_accepted+1;
   if(sv&&sq) mem_returned=mem_returned+1;
   if(returned>accepted || accepted-returned>1)$fatal(1,"CPU request/response conservation");
   if(mem_returned>mem_accepted || mem_accepted-mem_returned>1)$fatal(1,"memory outstanding conservation");
   if(mv && ma[3:0]!=0)$fatal(1,"unaligned memory line read");
   prev_valid=1;
  end
  prev_rst=rst;prev_state=state;prev_mq=mq;prev_sv=sv;
 end
endmodule

`default_nettype wire
