# Vivado non-project, out-of-context characterization. No board/pin/bitstream claim.
# FPGA_PART must identify a real part installed with the user's Vivado release.
if {![info exists ::env(FPGA_PART)] || $::env(FPGA_PART) eq ""} {
 error "Set FPGA_PART to the installed target part, e.g. the part on your board"
}
set here [file dirname [file normalize [info script]]]
set repo [file normalize [file join $here ../../../..]]
set variant region_buffer
if {[info exists ::env(CACHE_VARIANT)]} {set variant $::env(CACHE_VARIANT)}
set configs [dict create global_buffer {0 0 0} region_buffer {1 0 0} context_feedback {1 1 0} victim_buffer {0 0 1}]
if {![dict exists $configs $variant]} {error "Unknown CACHE_VARIANT $variant"}
lassign [dict get $configs $variant] region feedback victim
set period 10.0
if {[info exists ::env(CLOCK_PERIOD_NS)]} {set period $::env(CLOCK_PERIOD_NS)}
if {![string is double -strict $period] || $period<=0} {error "CLOCK_PERIOD_NS must be positive"}
set out [file join $repo Phase2 build vivado $variant]
file mkdir $out
set sources [list [file join $repo Phase1 level4 rtl stride_prefetcher.sv] \
 [file join $repo Phase2 level4 rtl region_stride_prefetcher.sv] \
 [file join $repo Phase2 level4 rtl ai_cache_context.sv] [file join $here fpga_cache_top.sv]]
read_verilog -sv $sources
synth_design -top fpga_cache_top -part $::env(FPGA_PART) -mode out_of_context \
 -generic [list REGION_ENABLE=$region FEEDBACK_ENABLE=$feedback VICTIM_ENABLE=$victim]
create_clock -name core_clk -period $period [get_ports clk]
# Explicit characterization assumptions, not board timing specifications.
set_clock_uncertainty 0.200 [get_clocks core_clk]
set inputs [remove_from_collection [all_inputs] [get_ports clk]]
set_input_delay -clock core_clk -min 0.500 $inputs
set_input_delay -clock core_clk -max 2.000 $inputs
set_output_delay -clock core_clk -min 0.500 [all_outputs]
set_output_delay -clock core_clk -max 2.000 [all_outputs]
# Synchronous reset stays timed. No blanket false paths or unconstrained clocks.
write_xdc -force [file join $out characterization.xdc]
report_utilization -hierarchical -file [file join $out utilization_synth.rpt]
report_timing_summary -delay_type min_max -report_unconstrained -file [file join $out timing_synth.rpt]
check_timing -verbose -file [file join $out check_timing.rpt]
report_methodology -file [file join $out methodology_synth.rpt]
report_drc -file [file join $out drc_synth.rpt]
write_checkpoint -force [file join $out post_synth.dcp]
if {[info exists ::env(RUN_IMPLEMENTATION)] && $::env(RUN_IMPLEMENTATION) eq "1"} {
 opt_design
 place_design
 phys_opt_design
 route_design
 report_utilization -file [file join $out utilization_routed.rpt]
 report_timing_summary -delay_type min_max -report_unconstrained -file [file join $out timing_routed.rpt]
 report_methodology -file [file join $out methodology_routed.rpt]
 report_drc -file [file join $out drc_routed.rpt]
 write_checkpoint -force [file join $out post_route.dcp]
 set setup_paths [get_timing_paths -delay_type max -max_paths 1]
 set hold_paths [get_timing_paths -delay_type min -max_paths 1]
 if {[llength $setup_paths]==0 || [llength $hold_paths]==0} {error "Missing timed paths"}
 if {[get_property SLACK $setup_paths]<0 || [get_property SLACK $hold_paths]<0} {error "Timing target failed"}
}
set f [open [file join $out run_metadata.txt] w]
puts $f "Vivado [version -short]\npart=$::env(FPGA_PART)\nvariant=$variant\nperiod_ns=$period\nmode=out_of_context\nI/O assumptions: min0.5ns max2.0ns; clock uncertainty0.2ns"
close $f
puts "Reports written to $out. Review DRC, methodology, unconstrained paths and timing before sign-off."
