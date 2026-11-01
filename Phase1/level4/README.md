# Level 4: RTL implementation and verification

This is the read-only Phase 1 subsystem: a 1 KiB direct-mapped cache, one queued demand, one memory transaction in flight and a selectable global stride/next-line predictor. Phase 2 changes are deliberately excluded.

Run all commands from `Phase1/`. The root Makefile builds the test programs into `build/verification/`; generated binaries, logs, waveforms and working results belong under `build/`.

## Start here

Open [the executed RTL walkthrough](rtl_walkthrough.ipynb). It reads the actual controller and runs the real verification commands. This folder contains the implementation, not placeholders.

```sh
# From the repository root
make rtl-test
```

A CPU hit registers one selected word. A miss saves one demand address. The controller moves through IDLE, SEND and WAIT, holds memory requests through backpressure and rechecks queued demands after speculative fills. [The architecture diagram](../level2/cache_architecture.svg) shows the data path.

| State | What happens | What ends the state |
|---|---|---|
| IDLE | Resolve queued demand or select an uncached prediction | A selected transaction |
| SEND | Hold aligned memory request and payload | Request valid and ready |
| WAIT | Receive one line and fill cache | Response valid and ready |


## Source map

| File | Responsibility |
|---|---|
| `rtl/ai_cache.sv` | Data/tag arrays, CPU response register, demand/candidate slots, memory FSM and counters |
| `rtl/stride_prefetcher.sv` | Signed repeated-delta predictor; ignores consecutive observations in one line |
| `rtl/next_line_prefetcher.sv` | Clocked reference predictor; proposes one following line per distinct accepted demand line |
| `tb/dram_model.sv` | Simulation-only deterministic backing data, request stalls and response delay |
| `tb/tb_cache.sv` | Legacy off/on workload and directed data/protocol checks; preserves original cycle measurements |
| `tb/tb_stress.sv` | 2,000 ordered continuously offered requests with consumer backpressure |
| `tb/tb_predictor.sv` | Stride training, signed arithmetic, bounds, repeated lines and enable checks |
| `tb/tb_next_line.sv` | Next-line enable/reset, distinct-line trigger, jumps and upper-bound checks |
| `tb/tb_trace.sv` | Shared timing/data checker for no-prefetch, stride and next-line comparisons |
| `tb/tb_adversarial.sv` | 10,000 ordered requests, four-line cache, severe CPU/memory stalls and mixed traffic |
| `tb/tb_nonpreemptible.sv` | Directed demonstration of demand waiting behind an already-selected prefetch |
| `synth/synth.ys`, `synth/next_line.ys` | Generic stride/next-line synthesis and structural checks; no target device/timing sign-off |

## Configuration and contract

- `INDEX_BITS=6` is the default: 64 slots, fixed 16-byte lines and 32-bit words. Supported index range is 1..27; practical simulations use small values.
- `PREFETCH_POLICY=1` selects stride; `2` selects next-line. Both use the same cache, registered candidate interface and controller. The simulation guard rejects other policy values.
- `prefetch_enable=0` suppresses new speculative selection. Predictor history continues training. A request already selected into SEND/WAIT is nonpreemptible and may finish after disable.
- Requests and responses transfer on rising edges with valid and ready asserted. Producers hold valid/payload while blocked.
- Read addresses must be naturally aligned 32-bit byte addresses. Backing data is immutable, read-only and noncoherent. There are no writes, exceptions, bus errors or virtual-memory protections.
- Reset is synchronous active high and must flush cache and memory together. Returning stale pre-reset memory responses after a cache-only reset is unsupported.

The fill-edge exclusion, demand recheck and original one-slot advisory candidate behavior are retained. A candidate arriving while an old slot is consumed may be dropped; this opportunity loss is not data corruption. Direct-map speculative fills can evict useful demand data. Keeping these limitations visible is part of the Phase 1 baseline.

## Trace replay interface

Compile the same testbench for either policy:

```sh
mkdir -p build/verification
iverilog -g2012 -Wall -s tb_trace \
  -Ptb_trace.PREFETCH_POLICY=1 -Ptb_trace.INDEX_BITS=6 -Ptb_trace.LATENCY=12 \
  -o build/verification/trace.vvp \
  level4/rtl/*.sv level4/tb/dram_model.sv level4/tb/tb_trace.sv
vvp build/verification/trace.vvp \
  +TRACE=/absolute/path/trace.mem +COUNT=512 +PF=1 \
  +OUT=build/verification/trace.csv
```

`PF=0` disables speculation. Each packed `.mem` row is 64 bits: byte address in `[63:32]`, compute gap in `[31:0]`. The input supports 1..65,536 aligned read observations and gaps 0..100,000. A gap is imposed only before a subsequent request, never after the final demand. Inputs with unknown rows, invalid alignment or oversized gaps fail.

The memory parameter is a countdown component, not the complete measured miss latency or physical DRAM timing. Request readiness periodically stalls, line-address-dependent jitter is added, and controller/model handshakes contribute cycles.

## Metrics and end-of-trace rules

All cycle and latency accumulators in `tb_trace` are 64 bits. A budget derived from row count, latency and actual gap sum replaces the original fixed global watchdog. Per-request timeouts bound unexpected stalls.

| CSV field | Definition |
|---|---|
| `cycles`, `completion_cycles` | Identical: cycles from post-reset experiment start to final CPU response consumption, including prior compute gaps and consumer stalls |
| `quiescent_cycles` | Time through natural speculative draining and two settled quiet edges |
| `latency_sum`, `max_latency` | Request acceptance to response availability; excludes consumer stalls after availability |
| `offer_latency_sum`, `max_offer_latency` | Request offer to response availability; includes preaccept waiting |
| `request_wait_cycles` | Sum of request offer-to-acceptance waits |
| `total_compute_gap_cycles` | Actual inter-demand gap cycles; final supplied gap excluded |
| `hits`, `misses` | Classification when a demand is accepted; prefetch traffic is not counted as demand accesses |
| `timely_useful` | First accepted demand hit on a prefetched-marked resident line |
| `late_useful` | Initially missed demand resolved by the controller's recheck of a speculative fill |
| `unused_evicted` | Prefetched-marked lines evicted without demand consumption |
| `resident_unconsumed` | Prefetched-marked lines still resident after draining |

Quiescence requires IDLE, no pending demand, no valid CPU response, no predictor candidate pulse, no pending candidate slot and no memory request/response. Two settled quiet edges cover the registered candidate pipeline. A fixed 100-cycle wait is insufficient when memory latency is increased.

The bench checks every returned word against `(address >> 2) XOR 0xcafe1234`, memory request stability and alignment, access classification and:

```text
prefetch_issued = timely_useful + late_useful + unused_evicted + resident_unconsumed
```

The hardware useful counter is timely only. Late/resident accounting is testbench instrumentation, not additional deployed hardware counters. `cycles` in the new trace CSV is not interchangeable with the legacy benchmark's cycles, which include a fixed final drain and final compute gap.

## Verification status and limits

The supplied legacy benches remain as regressions, while next-line, adversarial control and high-latency trace checks extend coverage. A three-line sequential trace at `LATENCY=128` requires more than 100 cycles after the last response to drain its final prefetch; the corrected trace bench handles it naturally.

Simulation and generic synthesis are bounded evidence. There is no formal proof, coverage closure, target FPGA bitstream, physical DRAM model, power measurement or timing closure. Resetting the data array and using combinational indexed reads favor small register/distributed-memory implementations rather than direct synchronous block-RAM inference.
