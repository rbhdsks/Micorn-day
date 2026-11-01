# Phase 1 release evidence

Validated 1 November 2026 on the `phase-1` branch, based on Nitesh's Level 1 commit `e0ab37c30e7a02dd1f3d868aef956ee88104a8b0`. This document describes executed checks; it does not certify organizer acceptance.

## Executed commands

```sh
make all
make synth YOSYS=/path/to/yowasp-yosys
make reference
```

Core CLI tools: Icarus Verilog/VVP 13.0 stable, Python 3.14.4, GNU Make 3.81. Synthesis: Yosys 0.70 through an isolated YoWASP installation. CI installs native Icarus/Yosys and can produce different generic cell counts with different tool versions.

| Check | Observed result |
|---|---|
| Imported Level 1 unit tests | 9 passed |
| Level 5 trace/metric/provenance unit tests | 11 passed |
| Legacy workload/directed RTL | 3,673 checked responses; original cycle results retained |
| Continuous-request stress | 2,000 ordered responses, 14,871 cycles |
| Independent small-cache stress | 10,000 ordered responses, 299,876 cycles |
| Stride and next-line units | Both passed |
| Nonpreemptible request demonstration | Accepted demand waited 20 cycles behind selected speculative request; protocol remained stable |
| High-latency/same-line replay smoke | 8 runs, 20 checked responses, both policies with PF off/on at LATENCY=128 |
| Three-policy Level 5 comparison | 13 traces x 3 policies = 39 passing runs; 16,944 checked responses |
| Generic stride synthesis | CHECK reports zero problems; 33,245 generic hierarchical cells |
| Generic next-line synthesis | CHECK reports zero problems; 32,877 generic hierarchical cells |

The workload/stress/smoke/benchmark runs above total **32,637 data-checked responses**, excluding predictor-only and directed limitation checks. The same addresses may occur in several tests; this is verification activity, not an independent statistical sample count.

## Representative measured completion results

| Trace | No prefetch cycles | Next-line cycles | Stride cycles | DRAM reads: none / next / stride |
|---|---:|---:|---:|---|
| Column stride | 21,098 | 21,098 | 12,573 | 512 / 1024 / 513 |
| Pollution return | 7,888 | 8,895 | 8,927 | 4 / 133 / 132 |
| Modelled matmul ijk A/B subset | 6,940 | 7,154 | 6,940 | 92 / 205 / 92 |
| Modelled matmul ikj A/B subset | 6,404 | 6,443 | 6,404 | 61 / 126 / 61 |

Speedup is baseline completion cycles / policy completion cycles. The end point is the final consumed demand response; speculative draining is separately published. These numbers intentionally differ from the older package's fixed-tail totals. In particular, there is no demonstrated stride acceleration on these two modelled matrix read subsets. Pollution and extra next-line traffic remain visible.

[Full measured comparisons](../level5/results/reference/report.md), [raw run CSVs/logs](../level5/results/reference/runs/), [run/source provenance](../level5/results/reference/provenance.json), and [generic synthesis excerpts](../level4/synth/reference/summary.json) are committed for review. The working build keeps full compilation, validation and synthesis logs; Git excludes generated binaries, waveforms and build directories.

## Remaining limits

No Phase 2 speculative buffer or feedback is implemented. No captured real-model trace, formal proof, coverage closure, FPGA bitstream, physical DRAM timing, target timing closure, power measurement or measured AI application speedup is claimed. The immutable A/B bridge and serial request/gap assumptions are explicit in Level 5 provenance. The independent audit's negative cases motivate the separate Phase 2 roadmap.

## Main branch publication expansion

The main-branch foundation now includes 8 cache-model tests, 6 predictor-model tests and 4 CDM arithmetic tests in addition to the original 20 Python checks, for **38 passing Python tests**. The existing 39 RTL benchmarks reproduce the retained measurements.

Five new portable walkthrough notebooks were executed with actual outputs. Nine scientific figure families are provided in PNG/PDF/SVG, alongside MATLAB plotting source. The report has 16 visually inspected pages, and the presentation has 23 slides with seven native editable charts and editable tables. The proposed CDM cache connection remains separate research. MATLAB scripts were not executed because MATLAB was unavailable.
