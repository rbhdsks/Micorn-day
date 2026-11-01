# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 512 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 512 |
| touched_line_footprint_bytes | 8192 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 12272 |
| adjacent_same_line_accesses | 0 |
| adjacent_same_line_fraction | 0.0 |
| accesses_to_previously_seen_line | 0 |
| mean_reuse_gap_accesses | None |

## Most accessed lines

| line_number | count |
|---|---|
| 256 | 1 |
| 257 | 1 |
| 258 | 1 |
| 259 | 1 |
| 260 | 1 |
| 261 | 1 |
| 262 | 1 |
| 263 | 1 |
| 264 | 1 |
| 265 | 1 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 1 | 511 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 1 | 511 |

## Reuse gaps

No observations.

## Most accessed regions

| region_number | count |
|---|---|
| 1 | 256 |
| 2 | 256 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
