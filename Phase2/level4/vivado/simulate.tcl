# Project-mode AMD xsim directed regressions. Launch from vivado -mode batch.
set here [file dirname [file normalize [info script]]]
set repo [file normalize [file join $here ../../../..]]
set out [file join $repo Phase2 build xsim]
file mkdir $out
create_project -force cache_xsim $out
set_property target_language Verilog [current_project]
add_files [list [file join $repo Phase1 level4 rtl stride_prefetcher.sv] \
 [file join $repo Phase2 level4 rtl region_stride_prefetcher.sv] \
 [file join $repo Phase2 level4 rtl ai_cache_context.sv]]
add_files -fileset sim_1 [list [file join $repo Phase1 level4 tb dram_model.sv] \
 [file join $repo Phase2 level4 tb context_protocol_monitor.sv] \
 [file join $repo Phase2 level4 tb tb_region_predictor.sv] \
 [file join $repo Phase2 level4 tb tb_context_directed.sv] \
 [file join $repo Phase2 level4 tb tb_victim_directed.sv] \
 [file join $repo Phase2 level4 audit_tests tb_independent.sv] \
 [file join $repo Phase2 level4 audit_tests context_sva.sv]]
set_property xsim.simulate.runtime all [get_filesets sim_1]
foreach top {tb_region_predictor tb_context_directed tb_victim_directed tb_independent} {
 set_property top $top [get_filesets sim_1]
 launch_simulation -simset sim_1 -mode behavioral
 close_sim
}
puts "Review each xsim simulation log for its PASS marker and any assertion/fatal."
