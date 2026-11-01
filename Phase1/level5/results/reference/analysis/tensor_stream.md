# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 512 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 128 |
| touched_line_footprint_bytes | 2048 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 6140 |
| adjacent_same_line_accesses | 384 |
| adjacent_same_line_fraction | 0.7514677103718199 |
| accesses_to_previously_seen_line | 384 |
| mean_reuse_gap_accesses | 1.0 |

## Most accessed lines

| line_number | count |
|---|---|
| 256 | 4 |
| 257 | 4 |
| 258 | 4 |
| 259 | 4 |
| 260 | 4 |
| 261 | 4 |
| 262 | 4 |
| 263 | 4 |
| 264 | 4 |
| 265 | 4 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 0 | 384 |
| 1 | 127 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 1 | 127 |

## Reuse gaps

| gap_accesses | count |
|---|---|
| 1 | 384 |

## Most accessed regions

| region_number | count |
|---|---|
| 1 | 512 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
