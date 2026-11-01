# Phase 1 measured RTL comparison

Cache: 1024 data bytes, 64 direct-mapped lines, 16 bytes per line. Memory model LATENCY=12; this is an internal countdown parameter, not physical DRAM latency.

All three modes replay the same demand addresses, post-response gaps, response-stall schedule and cache/memory geometry. none disables speculation; next_line and stride use distinct candidate generators through the same controller. Every returned word is checked against the deterministic backing-memory reference.

## Completion cycles and latency

| Trace | Policy | Demand hit rate | Mean accept→response | Mean offer→response | Completion cycles | Speedup | DRAM reads |
|---|---|---:|---:|---:|---:|---:|---:|
| column_stride | none | 0.00% | 17.746 | 17.746 | 21098 | 1.000× | 512 |
| column_stride | next_line | 0.00% | 17.746 | 17.746 | 21098 | 1.000× | 1024 |
| column_stride | stride | 99.41% | 1.096 | 1.096 | 12573 | 1.678× | 513 |
| embedding_gather | none | 3.91% | 17.424 | 17.424 | 12757 | 1.000× | 492 |
| embedding_gather | next_line | 3.52% | 25.406 | 25.416 | 16849 | 0.757× | 978 |
| embedding_gather | stride | 3.91% | 17.424 | 17.424 | 12757 | 1.000× | 492 |
| interleaved_conflicting | none | 0.00% | 18.059 | 18.059 | 21258 | 1.000× | 512 |
| interleaved_conflicting | next_line | 0.00% | 18.059 | 18.059 | 21258 | 1.000× | 1024 |
| interleaved_conflicting | stride | 0.00% | 18.059 | 18.059 | 21258 | 1.000× | 512 |
| modelled_matmul_ijk_ab_reads | none | 82.03% | 4.066 | 4.066 | 6940 | 1.000× | 92 |
| modelled_matmul_ijk_ab_reads | next_line | 82.42% | 4.475 | 4.484 | 7154 | 0.970× | 205 |
| modelled_matmul_ijk_ab_reads | stride | 82.03% | 4.066 | 4.066 | 6940 | 1.000× | 92 |
| modelled_matmul_ikj_ab_reads | none | 88.09% | 3.020 | 3.020 | 6404 | 1.000× | 61 |
| modelled_matmul_ikj_ab_reads | next_line | 90.04% | 3.092 | 3.096 | 6443 | 0.994× | 126 |
| modelled_matmul_ikj_ab_reads | stride | 88.09% | 3.020 | 3.020 | 6404 | 1.000× | 61 |
| phase_shift | none | 0.00% | 18.059 | 18.059 | 21258 | 1.000× | 512 |
| phase_shift | next_line | 49.80% | 9.406 | 9.406 | 16828 | 1.263× | 769 |
| phase_shift | stride | 98.83% | 1.197 | 1.197 | 12625 | 1.684× | 514 |
| pollution_return | none | 98.75% | 1.212 | 1.212 | 7888 | 1.000× | 4 |
| pollution_return | next_line | 79.38% | 4.359 | 4.359 | 8895 | 0.887× | 133 |
| pollution_return | stride | 78.75% | 4.459 | 4.459 | 8927 | 0.884× | 132 |
| same_line | none | 93.75% | 2.000 | 2.000 | 88 | 1.000× | 1 |
| same_line | next_line | 93.75% | 2.000 | 2.000 | 88 | 1.000× | 2 |
| same_line | stride | 93.75% | 2.000 | 2.000 | 88 | 1.000× | 1 |
| tensor_stream | none | 75.00% | 5.266 | 5.266 | 7554 | 1.000× | 128 |
| tensor_stream | next_line | 99.80% | 1.031 | 1.078 | 5410 | 1.396× | 129 |
| tensor_stream | stride | 99.41% | 1.102 | 1.146 | 5445 | 1.387× | 129 |
| three_line_bursts | none | 0.00% | 18.167 | 18.167 | 7980 | 1.000× | 192 |
| three_line_bursts | next_line | 66.67% | 6.495 | 6.495 | 5739 | 1.390× | 256 |
| three_line_bursts | stride | 0.00% | 18.167 | 18.167 | 7980 | 1.000× | 256 |
| tiled_reuse | none | 87.50% | 3.135 | 3.135 | 6463 | 1.000× | 64 |
| tiled_reuse | next_line | 99.80% | 1.031 | 1.059 | 5400 | 1.197× | 65 |
| tiled_reuse | stride | 99.41% | 1.102 | 1.127 | 5435 | 1.189× | 65 |
| two_stream_disjoint_sets | none | 0.00% | 18.369 | 18.369 | 21417 | 1.000× | 512 |
| two_stream_disjoint_sets | next_line | 0.00% | 18.369 | 18.369 | 21417 | 1.000× | 1024 |
| two_stream_disjoint_sets | stride | 0.00% | 18.369 | 18.369 | 21417 | 1.000× | 512 |
| zero_gap_stream | none | 0.00% | 18.369 | 18.369 | 11197 | 1.000× | 512 |
| zero_gap_stream | next_line | 0.00% | 14.633 | 14.633 | 9284 | 1.206× | 513 |
| zero_gap_stream | stride | 0.00% | 14.643 | 14.643 | 9289 | 1.205× | 513 |

## Prefetch outcomes

| Trace | Policy | Issued | Timely | Late | Unused evicted | Resident | Consumption accuracy | DRAM overhead |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| column_stride | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| column_stride | next_line | 512 | 0 | 0 | 496 | 16 | 0.00% | +100.00% |
| column_stride | stride | 510 | 509 | 0 | 0 | 1 | 99.80% | +0.20% |
| embedding_gather | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| embedding_gather | next_line | 484 | 8 | 0 | 445 | 31 | 1.65% | +98.78% |
| embedding_gather | stride | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| interleaved_conflicting | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| interleaved_conflicting | next_line | 512 | 0 | 0 | 511 | 1 | 0.00% | +100.00% |
| interleaved_conflicting | stride | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| modelled_matmul_ijk_ab_reads | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| modelled_matmul_ijk_ab_reads | next_line | 115 | 38 | 0 | 74 | 3 | 33.04% | +122.83% |
| modelled_matmul_ijk_ab_reads | stride | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| modelled_matmul_ikj_ab_reads | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| modelled_matmul_ikj_ab_reads | next_line | 75 | 29 | 0 | 44 | 2 | 38.67% | +106.56% |
| modelled_matmul_ikj_ab_reads | stride | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| phase_shift | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| phase_shift | next_line | 512 | 255 | 0 | 241 | 16 | 49.80% | +50.20% |
| phase_shift | stride | 508 | 506 | 0 | 1 | 1 | 99.61% | +0.39% |
| pollution_return | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| pollution_return | next_line | 67 | 2 | 0 | 64 | 1 | 2.99% | +3225.00% |
| pollution_return | stride | 64 | 0 | 0 | 64 | 0 | 0.00% | +3200.00% |
| same_line | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| same_line | next_line | 1 | 0 | 0 | 0 | 1 | 0.00% | +100.00% |
| same_line | stride | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| tensor_stream | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| tensor_stream | next_line | 128 | 127 | 0 | 0 | 1 | 99.22% | +0.78% |
| tensor_stream | stride | 126 | 125 | 0 | 0 | 1 | 99.21% | +0.78% |
| three_line_bursts | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| three_line_bursts | next_line | 192 | 128 | 0 | 63 | 1 | 66.67% | +33.33% |
| three_line_bursts | stride | 64 | 0 | 0 | 63 | 1 | 0.00% | +33.33% |
| tiled_reuse | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| tiled_reuse | next_line | 64 | 63 | 0 | 0 | 1 | 98.44% | +1.56% |
| tiled_reuse | stride | 62 | 61 | 0 | 0 | 1 | 98.39% | +1.56% |
| two_stream_disjoint_sets | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| two_stream_disjoint_sets | next_line | 512 | 0 | 0 | 511 | 1 | 0.00% | +100.00% |
| two_stream_disjoint_sets | stride | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| zero_gap_stream | none | 0 | 0 | 0 | 0 | 0 | N/A | +0.00% |
| zero_gap_stream | next_line | 512 | 0 | 511 | 0 | 1 | 99.80% | +0.20% |
| zero_gap_stream | stride | 510 | 0 | 509 | 0 | 1 | 99.80% | +0.20% |

## Definitions and interpretation limits

- Demand hit rate = demand hits / total demand accesses. Prefetch transactions are never added to either demand count.
- Speedup = no-prefetch completion cycles / policy completion cycles. Completion ends at final demand response consumption and excludes the final unused compute gap. Earlier gaps and consumer stalls remain part of the offered workload.
- quiescent_cycles additionally includes bounded natural draining of predictor/candidate/controller state; no fixed padding is added. summary.csv publishes both cycle definitions and both ratios.
- Accept-to-response latency ends when data becomes available and excludes consumer stalls afterward. Offer-to-response additionally includes request waiting before acceptance. Consumer stalls still affect completion cycles.
- The driver serializes reads, then waits the trace gap. Gap zero does not mean a fully pipelined one-request-per-cycle processor.
- Consumption accuracy = (first timely consumption + late consumption) / issued prefetch reads. Resident lines remain unresolved but stay in the denominator. N/A means no prefetch was issued.
- At quiescence: issued = timely + late + unused evicted + resident. Raw run CSVs record all terms. unused_evicted is not by itself a measurement of demand-cache pollution.
- Total memory traffic includes demand and prefetch reads. Bytes = 16 × transactions for this fixed-line simulation, not measured DDR bandwidth.
- Synthetic patterns are diagnostic examples. modelled_matmul traces preserve only logical immutable A/B compute reads from Nitesh’s Level 1 generator; C, writes and initialization are excluded. They are not captured instructions, a complete inference trace or application timing.
- Matmul numeric correctness is checked by the Level 1 generator. RTL replay uses address-derived memory words, so it checks data transport rather than executing the numeric matmul.
- One fixed irregular seed is provided. Deterministic reruns establish reproducibility, not statistical confidence or a universal speedup.
- Phase 1 intentionally retains direct-map speculative insertion and a global single-stride predictor. Pollution, useless short-burst predictions and interleaved-stream failures are exposed, not hidden. Buffering/feedback upgrades belong to Phase 2.
- Comparisons against the older audited package need care: old cycle counts included fixed drains and the final gap. The cycle definition here is explicitly different.

## Evidence files

`summary.csv` contains full derived metrics. `runs/` contains each simulator CSV and transcript. `analysis/` contains 16-byte-line Level 1 summaries. `traces/manifest.json` records provenance and checksums. `provenance.json` records commands, parameters, source hashes and tool versions.
