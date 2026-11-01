`timescale 1ns/1ps
`default_nettype none
module tb_region_predictor;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,en=1,observe=0;
 reg[27:0] line_addr=0;
 wire candidate_valid;wire[27:0] candidate_line;
 region_stride_prefetcher dut(clk,rst,en,observe,line_addr,candidate_valid,candidate_line);
 integer checked=0;
 task step(input[27:0] line,input bit expected_valid,input[27:0] expected_line);
 begin
  @(negedge clk);observe=1;line_addr=line;
  @(negedge clk);observe=0;
  if(candidate_valid!==expected_valid) $fatal(1,"region valid line=%h expected=%b actual=%b",line,expected_valid,candidate_valid);
  if(expected_valid && candidate_line!==expected_line) $fatal(1,"region candidate line=%h expected=%h actual=%h",line,expected_line,candidate_line);
  checked=checked+1;
 end endtask
 task reset_predictor;
 begin @(negedge clk);rst=1;repeat(2)@(negedge clk);rst=0;end
 endtask
 initial begin
  repeat(3)@(negedge clk);rst=0;
  step('h100,0,0);step('h1000,0,0);
  step('h104,0,0);step('h1004,0,0);
  step('h108,1,'h10c);step('h1008,1,'h100c);
  step('h108,0,0); // repeated same-region line does not retrain
  en=0;step('h10c,0,0);en=1;step('h110,1,'h114); // disable still trains
  step('h1010,0,0);step('h100c,0,0);step('h1008,1,'h1004); // signed reversal
  reset_predictor();
  step(2,0,0);step(1,0,0);step(0,0,0); // reject negative predicted line
  reset_predictor();
  step('hffffffd,0,0);step('hffffffe,0,0);step('hfffffff,0,0); // reject overflow
  reset_predictor();
  step('h100,0,0);step('h104,0,0);step('h108,1,'h10c);
  step('h200,0,0);step('h300,0,0);step('h400,0,0);step('h500,0,0);
  step('h10c,0,0); // fifth distinct region evicted original history
  step('h110,0,0);step('h114,1,'h118);
  reset_predictor();step('h0fe,0,0);step('h0ff,0,0);step('h100,0,0); // boundary retrains
  $display("PASS: region predictor %0d checked observations",checked);$finish;
 end
 initial begin #100000;$fatal(1,"region predictor watchdog");end
endmodule

`default_nettype wire
