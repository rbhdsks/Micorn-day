# AMD Vivado and FPGA characterization

These scripts prepare the design for a supported AMD Vivado host. Vivado, xvlog, xelab and xsim are **not installed on this macOS authoring host**, so this flow is supplied but not executed. Icarus and Verilator simulation evidence is separate from AMD simulator evidence. No timing closure, board operation or Micron internal sign-off is claimed.

```sh
# From repository root, after sourcing your installed Vivado settings script
vivado -mode batch -source Phase2/level4/vivado/simulate.tcl
FPGA_PART=YOUR_INSTALLED_PART CACHE_VARIANT=region_buffer CLOCK_PERIOD_NS=10 \
  vivado -mode batch -source Phase2/level4/vivado/characterize.tcl
# Optional placement/routing characterization, still without a board bitstream
FPGA_PART=YOUR_INSTALLED_PART RUN_IMPLEMENTATION=1 \
  vivado -mode batch -source Phase2/level4/vivado/characterize.tcl
```

The functional wrapper disconnects debug statistics so synthesis can prune instrumentation. The Tcl records the part, tool version, target clock and assumptions. It leaves synchronous reset timed and reports unconstrained paths, utilization, DRC and methodology findings. It intentionally has no board pin assignments or blanket false path exceptions. The default10ns clock and0.5/2ns I/O delays are characterization assumptions that an integrator must replace with interface timing requirements. Placement/routing does not establish hardware correctness, and a positive setup slack alone does not establish a complete sign-off.

AMD's [UG900 simulator reference](https://docs.amd.com/r/2021.1-English/ug900-vivado-logic-simulation/Vivado-Simulator-Quick-Reference-Guide) describes the xvlog, xelab and xsim stages. [UG901 FSM registers](https://docs.amd.com/r/2022.2-English/ug901-vivado-synthesis/FSM-Registers) recommends a defined reset state and synchronous FSM reset. [UG949 startup guidance](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Controlling-and-Synchronizing-Device-Startup) explains why device startup and reset release need deliberate control. These public engineering references are not a Micron qualification checklist.

The current design is a single clock subsystem with no asynchronous input synchronization. A physical board top needs synchronized reset release, clock generation, CDC at any foreign interface, a documented memory adapter and exact pin/I/O constraints. The combinational small-cache lookup has no promised block RAM inference. Converting to synchronous block RAM requires a pipelined lookup and new latency verification.
