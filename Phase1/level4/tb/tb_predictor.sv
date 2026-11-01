`timescale 1ns/1ps
module tb_predictor;
 reg clk=0;always #5 clk=~clk;
 reg rst=1, enable=1, observe=0;
 reg [27:0] line_addr=0;
 wire candidate_valid; wire [27:0] candidate_line;
 stride_prefetcher dut(clk,rst,enable,observe,line_addr,candidate_valid,candidate_line);
 task automatic reset_p;
  begin @(negedge clk);rst=1;observe=0;enable=1;@(negedge clk);rst=0;end
 endtask
 task automatic sample(input [27:0] a,input bit v,input [27:0] p);
  begin
   @(negedge clk);observe=1;line_addr=a;
   @(posedge clk);#1;
   if(candidate_valid!==v || (v && candidate_line!==p))
    $fatal(1,"predictor line=%h valid=%b predicted=%h expected=%h",a,candidate_valid,candidate_line,p);
  end
 endtask
 initial begin
  reset_p;
  sample(10,0,0);sample(11,0,0);sample(11,0,0);sample(12,1,13);
  sample(13,1,14);sample(20,0,0);sample(27,1,34);
  reset_p;
  sample(30,0,0);sample(20,0,0);sample(10,1,0);sample(0,0,0);
  reset_p;
  sample(28'hffffffd,0,0);sample(28'hffffffe,0,0);sample(28'hfffffff,0,0);
  reset_p;
  enable=0;sample(10,0,0);sample(11,0,0);sample(12,0,0);
  enable=1;sample(13,1,14);
  @(negedge clk);observe=0;@(posedge clk);#1;
  if(candidate_valid) $fatal(1,"candidate must be a pulse");
  $display("PASS: predictor training, repeated lines, phase change, signed stride, bounds and disable");$finish;
 end
endmodule
