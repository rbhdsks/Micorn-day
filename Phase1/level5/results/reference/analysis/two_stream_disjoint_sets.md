# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 512 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 512 |
| touched_line_footprint_bytes | 8192 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 270320 |
| adjacent_same_line_accesses | 0 |
| adjacent_same_line_fraction | 0.0 |
| accesses_to_previously_seen_line | 0 |
| mean_reuse_gap_accesses | None |

## Most accessed lines

| line_number | count |
|---|---|
| 256 | 1 |
| 16385 | 1 |
| 258 | 1 |
| 16387 | 1 |
| 260 | 1 |
| 16389 | 1 |
| 262 | 1 |
| 16391 | 1 |
| 264 | 1 |
| 16393 | 1 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 16129 | 256 |
| -16127 | 255 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 16129 | 256 |
| -16127 | 255 |

## Reuse gaps

No observations.

## Most accessed regions

| region_number | count |
|---|---|
| 1 | 128 |
| 64 | 128 |
| 2 | 128 |
| 65 | 128 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
