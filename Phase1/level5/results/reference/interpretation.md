# Why each measured result occurs

All numbers below use the retained RTL completion metric. Explanations identify mechanisms, not general application-speedup claims.

## column_stride

A repeated +4-line pitch trains stride; next-line fetches the wrong intervening lines. Compute gaps can hide that traffic but do not make it free.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 0 / 512 | 21098 | 1.000x | 512 |
| next_line | 0 / 512 | 21098 | 1.000x | 1024 |
| stride | 509 / 512 | 12573 | 1.678x | 513 |

## embedding_gather

This fixed seed does not qualify the stride pattern. Next-line mostly speculates incorrectly and increases exposed latency and traffic.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 20 / 512 | 12757 | 1.000x | 492 |
| next_line | 18 / 512 | 16849 | 0.757x | 978 |
| stride | 20 / 512 | 12757 | 1.000x | 492 |

## interleaved_conflicting

Alternating streams destroy global-stride repetition; corresponding bases also share cache indices. Next-line produces wrong/timing-sensitive speculative fills.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 0 / 512 | 21258 | 1.000x | 512 |
| next_line | 0 / 512 | 21258 | 1.000x | 1024 |
| stride | 0 / 512 | 21258 | 1.000x | 512 |

## modelled_matmul_ijk_ab_reads

Individual operands are regular, but the combined A/B history does not give this global stride policy a useful measured gain. Next-line adds substantial traffic.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 420 / 512 | 6940 | 1.000x | 92 |
| next_line | 422 / 512 | 7154 | 0.970x | 205 |
| stride | 420 / 512 | 6940 | 1.000x | 92 |

## modelled_matmul_ikj_ab_reads

Existing spatial reuse already serves most requests. Next-line adds some hits but more traffic and slightly longer completion; stride is unchanged.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 451 / 512 | 6404 | 1.000x | 61 |
| next_line | 461 / 512 | 6443 | 0.994x | 126 |
| stride | 451 / 512 | 6404 | 1.000x | 61 |

## phase_shift

Both long phases provide repeated regular deltas. Stride retrains after the change, with cold/retraining and unused-prediction costs.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 0 / 512 | 21258 | 1.000x | 512 |
| next_line | 255 / 512 | 16828 | 1.263x | 769 |
| stride | 506 / 512 | 12625 | 1.684x | 514 |

## pollution_return

A prediction of 0x1400 evicts hot 0x1000 at index zero. Repeated wrong fills cause extra demand misses; the paired baseline establishes pollution.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 316 / 320 | 7888 | 1.000x | 4 |
| next_line | 254 / 320 | 8895 | 0.887x | 133 |
| stride | 252 / 320 | 8927 | 0.884x | 132 |

## same_line

All accesses use one line. Next-line cannot improve the already-resident demand sequence and leaves one extra speculative read.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 15 / 16 | 88 | 1.000x | 1 |
| next_line | 15 / 16 | 88 | 1.000x | 2 |
| stride | 15 / 16 | 88 | 1.000x | 1 |

## tensor_stream

Four words share a line, so baseline already hits 75 percent. Next-line starts earlier than stride; both reduce exposed line-boundary waits.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 384 / 512 | 7554 | 1.000x | 128 |
| next_line | 511 / 512 | 5410 | 1.396x | 129 |
| stride | 509 / 512 | 5445 | 1.387x | 129 |

## three_line_bursts

Stride qualifies at the final line of each burst and fetches unused data. Next-line starts after the first line and supplies later lines, despite equal total speculative traffic.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 0 / 192 | 7980 | 1.000x | 192 |
| next_line | 128 / 192 | 5739 | 1.390x | 256 |
| stride | 0 / 192 | 7980 | 1.000x | 256 |

## tiled_reuse

Baseline reuses each tile. Prediction helps mainly on first visits to its lines; startup explains next-line versus stride differences.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 448 / 512 | 6463 | 1.000x | 64 |
| next_line | 511 / 512 | 5400 | 1.197x | 65 |
| stride | 509 / 512 | 5435 | 1.189x | 65 |

## two_stream_disjoint_sets

The stream sets avoid interstream index conflicts, yet global history still alternates incompatible deltas. This isolates a predictor limitation; next-line wastes traffic.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 0 / 512 | 21417 | 1.000x | 512 |
| next_line | 0 / 512 | 21417 | 1.000x | 1024 |
| stride | 0 / 512 | 21417 | 1.000x | 512 |

## zero_gap_stream

Predictions arrive after demand acceptance but earlier than a new demand read would. Late consumption shortens misses without producing timely hits.

| Policy | Hits / accesses | Completion cycles | Speedup | DRAM reads |
|---|---:|---:|---:|---:|
| none | 0 / 512 | 11197 | 1.000x | 512 |
| next_line | 0 / 512 | 9284 | 1.206x | 513 |
| stride | 0 / 512 | 9289 | 1.205x | 513 |
