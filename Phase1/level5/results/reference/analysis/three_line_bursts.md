# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 192 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 192 |
| touched_line_footprint_bytes | 3072 |
| minimum_byte_address | 65536 |
| maximum_byte_address | 323616 |
| adjacent_same_line_accesses | 0 |
| adjacent_same_line_fraction | 0.0 |
| accesses_to_previously_seen_line | 0 |
| mean_reuse_gap_accesses | None |

## Most accessed lines

| line_number | count |
|---|---|
| 4096 | 1 |
| 4097 | 1 |
| 4098 | 1 |
| 4352 | 1 |
| 4353 | 1 |
| 4354 | 1 |
| 4608 | 1 |
| 4609 | 1 |
| 4610 | 1 |
| 4864 | 1 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 1 | 128 |
| 254 | 63 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 1 | 128 |
| 254 | 63 |

## Reuse gaps

No observations.

## Most accessed regions

| region_number | count |
|---|---|
| 16 | 3 |
| 17 | 3 |
| 18 | 3 |
| 19 | 3 |
| 20 | 3 |
| 21 | 3 |
| 22 | 3 |
| 23 | 3 |
| 24 | 3 |
| 25 | 3 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
