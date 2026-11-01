# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 16 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 1 |
| touched_line_footprint_bytes | 16 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 4108 |
| adjacent_same_line_accesses | 15 |
| adjacent_same_line_fraction | 1.0 |
| accesses_to_previously_seen_line | 15 |
| mean_reuse_gap_accesses | 1.0 |

## Most accessed lines

| line_number | count |
|---|---|
| 256 | 16 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 0 | 15 |

## Line transitions (zero deltas excluded)

No observations.

## Reuse gaps

| gap_accesses | count |
|---|---|
| 1 | 15 |

## Most accessed regions

| region_number | count |
|---|---|
| 1 | 16 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
