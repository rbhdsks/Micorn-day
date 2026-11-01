# Verification and measurement gates

Run `make test` from the repository root. A nonzero simulator exit or missing PASS marker fails the run; transcripts are retained under `Phase1/build/verification/`. A failed benchmark command must not be treated as successful evidence.

| Gate | Checks |
|---|---|
| Level 1 Python tests | Address parsing, locality/reuse statistics, generated matrix results and address bounds |
| Level 5 tooling tests | Strict replay format, bounds, filter provenance, outcome conservation, paired metrics, report edge cases |
| `tb_cache` | 3,673 returned words; streams, reuse, irregular accesses, word offsets, conflicts, shared in-flight reset and runtime disable |
| `tb_stress` | 2,000 ordered responses with continuous requests, independent consumer stalls and enable toggling |
| `tb_predictor` | Repeated-delta threshold, same-line filtering, signed stride, bounds and disabled output |
| `tb_next_line` | Next-line startup, repeats, top-address suppression, disable and reset |
| `tb_adversarial` | 10,000 ordered responses in a four-line cache; full-address/conflict/random traffic and long independent stalls |
| `tb_nonpreemptible` | Demonstrates a queued demand waiting behind a selected, unaccepted prefetch without violating ready/valid |
| `tools/trace_smoke.py` | Both policies, PF off/on, three-line and same-line traces at LATENCY=128; natural tail exceeds the old 100-cycle assumption |
| Full Level 5 replay | Same inputs/geometry/stalls for none, next-line and stride; every returned word checked; outcomes conserved after natural drain |
| Generic synthesis | Both static policy selections pass Yosys hierarchy/synth/check/stat; target timing/FPGA are separate |

The original `tb_cache` retains its original fixed 50-cycle drain strictly to preserve its historical regression counters/cycles. New performance claims use `tb_trace` with separate last-demand completion and bounded natural quiescence. Do not mix those cycle definitions.

The trace bench waits for two settled quiet edges, including the registered predictor candidate, pending candidate, memory FSM, demand slot and response channels. It uses wide cycle/latency accumulators and an input-derived watchdog. Outcome identity at quiescence is `issued = timely + late + unused_evicted + resident_unconsumed`. Late/resident counts are testbench instrumentation, not new deployed hardware ports.

The independent reference word is `(byte_address >> 2) XOR 0xcafe1234`. The RTL check verifies address/line/word selection and ordered data delivery; it does not execute the numerical matrix multiplication. Matrix arithmetic is independently checked in the Level 1 generator.

Simulation is bounded evidence, not formal proof or exhaustive coverage. The main stress/probe seeds are deterministic; no statistical-confidence claim follows from rerunning the same input. Shared endpoint reset is supported; cache-only reset with stale responses, writes, coherence and memory errors are outside scope. Functional coverage closure, target timing, board integration and realistic DRAM scheduling remain future work.
