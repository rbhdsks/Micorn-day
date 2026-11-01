# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 9 |
| line_size_bytes | 64 |
| region_size_bytes | 4096 |
| unique_cache_lines | 4 |
| touched_line_footprint_bytes | 256 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 4288 |
| adjacent_same_line_accesses | 1 |
| adjacent_same_line_fraction | 0.125 |
| accesses_to_previously_seen_line | 5 |
| mean_reuse_gap_accesses | 3.4 |
| source_path | level1/examples/synthetic_sequential.txt |
| trace_format | text |

## Most accessed lines

| line_number | count |
|---|---|
| 64 | 3 |
| 65 | 2 |
| 66 | 2 |
| 67 | 2 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 1 | 6 |
| 0 | 1 |
| -3 | 1 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 1 | 6 |
| -3 | 1 |

## Reuse gaps

| gap_accesses | count |
|---|---|
| 4 | 4 |
| 1 | 1 |

## Most accessed regions

| region_number | count |
|---|---|
| 1 | 9 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
