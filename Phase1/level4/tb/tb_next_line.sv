`timescale 1ns/1ps
module tb_next_line;
 reg clk=0;always #5 clk=~clk;
 reg rst=1,enable=1,observe=0;
 reg [27:0] line_addr=0;
 wire candidate_valid;
 wire [27:0] candidate_line;
 next_line_prefetcher dut(clk,rst,enable,observe,line_addr,candidate_valid,candidate_line);
 task automatic sample(input [27:0] a,input bit expected_valid,input [27:0] expected_line);
  begin
   @(negedge clk);observe=1;line_addr=a;
   @(posedge clk);#1;
   if(candidate_valid!==expected_valid || (expected_valid && candidate_line!==expected_line))
    $fatal(1,"next-line mismatch line=%h valid=%b candidate=%h",a,candidate_valid,candidate_line);
  end
 endtask
 initial begin
  repeat(3)@(negedge clk);rst=0;
  sample(10,1,11);sample(10,0,0);sample(14,1,15);
  sample(28'hfffffff,0,0);sample(0,1,1);
  enable=0;sample(100,0,0);
  enable=1;sample(100,0,0);sample(101,1,102);
  @(negedge clk);observe=0;@(posedge clk);#1;
  if(candidate_valid)$fatal(1,"candidate must clear without an observation");
  @(negedge clk);rst=1;@(posedge clk);#1;
  if(candidate_valid || candidate_line!=0)$fatal(1,"reset failed");
  @(negedge clk);rst=0;sample(28'hffffffe,1,28'hfffffff);
  $display("PASS: next-line distinct observations, arbitrary jumps, enable, upper bound and reset");$finish;
 end
 initial begin #100000;$fatal(1,"next-line watchdog");end
endmodule
