`timescale 1ns/1ps
module tb_cache;
 parameter INDEX_BITS=6;
 reg clk=0; always #5 clk=~clk;
 reg rst=1, enable=0;
 reg cv=0, cr=0;
 reg [31:0] ca=0;
 wire cq, rv;
 wire [31:0] rd;
 wire mv,mq,sv,sq;
 wire [31:0] ma;
 wire [127:0] sd;
 wire [31:0] accesses,hits,misses,issued,useful,unused,reads;
 ai_cache #(.INDEX_BITS(INDEX_BITS)) dut(clk,rst,enable,cv,cq,ca,rv,cr,rd,mv,mq,ma,sv,sq,sd,accesses,hits,misses,issued,useful,unused);
 dram_model dram(clk,rst,mv,mq,ma,sv,sq,sd,reads);
 integer cycles=0, checked=0, fd, start_cycle, mode, k, w, delay_cycles;
 reg [31:0] addr, rng;
 string workload;
 always @(posedge clk) cycles<=cycles+1;
 initial begin #20000000; $fatal(1,"global watchdog"); end
 task automatic reset_system(input bit en);
  begin
   @(negedge clk); rst=1; cv=0; cr=0; enable=en;
   repeat(4) @(negedge clk);
   rst=0;
   repeat(2) @(negedge clk);
  end
 endtask
 task automatic read_word(input [31:0] a, input integer stall, input integer gap);
  integer watchdog, j;
  reg [31:0] expected, held;
  begin
   expected=(a>>2)^32'hcafe1234;
   @(negedge clk); ca=a; cv=1; cr=0; watchdog=0;
   do begin
    @(posedge clk); watchdog=watchdog+1;
    if(watchdog>500) $fatal(1,"request timeout");
   end while(!cq);
   @(negedge clk); cv=0;
   watchdog=0;
   while(!rv) begin
    @(negedge clk); watchdog=watchdog+1;
    if(watchdog>500) $fatal(1,"response timeout");
   end
   if(rd!==expected) $fatal(1,"data mismatch a=%h expected=%h got=%h",a,expected,rd);
   held=rd;
   for(j=0;j<stall;j=j+1) begin
    @(negedge clk);
    if(!rv || rd!==held) $fatal(1,"response changed under backpressure");
   end
   cr=1;
   @(negedge clk); cr=0; checked=checked+1;
   repeat(gap) @(negedge clk);
  end
 endtask
 // Memory request must remain stable until accepted.
 reg blocked=0;
 reg [31:0] held_addr;
 always @(posedge clk) begin
  if(rst) blocked<=0;
  else begin
   if(blocked && (!mv || ma!==held_addr)) $fatal(1,"memory request unstable");
   blocked<=mv && !mq; held_addr<=ma;
   if(mv && ma[3:0]!=0) $fatal(1,"unaligned memory request");
  end
 end
 initial begin
  if($test$plusargs("wave")) begin $dumpfile("build/verification/cache.vcd"); $dumpvars(0,tb_cache); end
  fd=$fopen("build/verification/metrics.csv","w");
  $fdisplay(fd,"workload,prefetch,accesses,hits,misses,prefetch_issued,prefetch_useful,prefetch_unused_evicted,dram_reads,cycles");
  for(w=0;w<7;w=w+1) begin
   case(w)
    0: workload="sequential";
    1: workload="stride_64B";
    2: workload="reverse";
    3: workload="reuse";
    4: workload="random";
    5: workload="no_compute_gap";
    6: workload="phase_change";
   endcase
   for(mode=0;mode<2;mode=mode+1) begin
    reset_system(mode!=0); rng=32'h12345678; start_cycle=cycles;
    for(k=0;k<256;k=k+1) begin
     rng=rng^(rng<<13); rng=rng^(rng>>17); rng=rng^(rng<<5);
     delay_cycles=20;
     case(w)
      0: addr=32'h1000+k*16;
      1: addr=32'h4000+k*64;
      2: addr=32'h8000-k*16;
      3: addr=32'h1000+(k%32)*4;
      4: addr=32'h1000+(rng%1024)*4;
      5: begin addr=32'h1000+k*16; delay_cycles=0; end
      6: if(k<128) addr=32'h1000+k*16; else addr=32'h4000+(k-128)*64;
     endcase
     read_word(addr,k%4,delay_cycles);
    end
    // Drain speculative activity; included in cycles/traffic for both modes.
    repeat(50) @(negedge clk);
    if(accesses!==256 || hits+misses!==accesses) $fatal(1,"counter accounting");
    if(mode==0 && issued!=0) $fatal(1,"disabled prefetch generated traffic");
    if(w<3 && mode==1 && useful<200) $fatal(1,"predictor failed regular stream");
    $fdisplay(fd,"%s,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",workload,mode,accesses,hits,misses,issued,useful,unused,reads,cycles-start_cycle);
    $display("%s pf=%0d hits=%0d misses=%0d pf_useful=%0d reads=%0d cycles=%0d",workload,mode,hits,misses,useful,reads,cycles-start_cycle);
   end
  end
  // All word offsets, conflict replacements and boundary wrap rejection.
  reset_system(1);
  for(k=0;k<64;k=k+1) read_word(32'h2000+(k%4)*4+(k%2)*4096,5,0);
  read_word(32'hffffffe0,0,20); read_word(32'hfffffff0,0,20);
  read_word(0,0,20); read_word(16,0,20);
  // Reset while demand memory operation is active (both endpoints reset).
  reset_system(1);
  @(negedge clk); cv=1; ca=32'h1000;
  do @(posedge clk); while(!cq);
  @(negedge clk); cv=0;
  wait(mv && mq); @(negedge clk);
  reset_system(0); read_word(32'h1000,3,0);
  // Runtime disabling: pending/accepted memory operations may finish.
  reset_system(1);
  for(k=0;k<10;k=k+1) read_word(32'h1000+k*16,0,20);
  @(negedge clk); enable=0;
  for(k=10;k<20;k=k+1) read_word(32'h1000+k*16,0,0);
  $fclose(fd);
  $display("PASS: %0d verified responses; all directed checks passed",checked);
  $finish;
 end
endmodule
