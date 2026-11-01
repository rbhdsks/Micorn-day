# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 320 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 4 |
| touched_line_footprint_bytes | 64 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 5104 |
| adjacent_same_line_accesses | 63 |
| adjacent_same_line_fraction | 0.1974921630094044 |
| accesses_to_previously_seen_line | 316 |
| mean_reuse_gap_accesses | 4.0 |

## Most accessed lines

| line_number | count |
|---|---|
| 256 | 128 |
| 317 | 64 |
| 318 | 64 |
| 319 | 64 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 1 | 128 |
| 61 | 64 |
| -63 | 64 |
| 0 | 63 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 1 | 128 |
| 61 | 64 |
| -63 | 64 |

## Reuse gaps

| gap_accesses | count |
|---|---|
| 5 | 189 |
| 4 | 64 |
| 1 | 63 |

## Most accessed regions

| region_number | count |
|---|---|
| 1 | 320 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
