# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 512 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 512 |
| touched_line_footprint_bytes | 8192 |
| minimum_byte_address | 65536 |
| maximum_byte_address | 98240 |
| adjacent_same_line_accesses | 0 |
| adjacent_same_line_fraction | 0.0 |
| accesses_to_previously_seen_line | 0 |
| mean_reuse_gap_accesses | None |

## Most accessed lines

| line_number | count |
|---|---|
| 4096 | 1 |
| 4100 | 1 |
| 4104 | 1 |
| 4108 | 1 |
| 4112 | 1 |
| 4116 | 1 |
| 4120 | 1 |
| 4124 | 1 |
| 4128 | 1 |
| 4132 | 1 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 4 | 511 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 4 | 511 |

## Reuse gaps

No observations.

## Most accessed regions

| region_number | count |
|---|---|
| 16 | 64 |
| 17 | 64 |
| 18 | 64 |
| 19 | 64 |
| 20 | 64 |
| 21 | 64 |
| 22 | 64 |
| 23 | 64 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
