# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 512 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 24 |
| touched_line_footprint_bytes | 384 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 8444 |
| adjacent_same_line_accesses | 0 |
| adjacent_same_line_fraction | 0.0 |
| accesses_to_previously_seen_line | 488 |
| mean_reuse_gap_accesses | 13.80327868852459 |

## Most accessed lines

| line_number | count |
|---|---|
| 256 | 32 |
| 257 | 32 |
| 258 | 32 |
| 259 | 32 |
| 260 | 32 |
| 261 | 32 |
| 262 | 32 |
| 263 | 32 |
| 512 | 16 |
| 513 | 16 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 257 | 20 |
| 259 | 20 |
| 261 | 20 |
| 263 | 20 |
| -257 | 19 |
| -259 | 19 |
| -261 | 19 |
| -263 | 19 |
| -256 | 17 |
| -258 | 17 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 257 | 20 |
| 259 | 20 |
| 261 | 20 |
| 263 | 20 |
| -257 | 19 |
| -259 | 19 |
| -261 | 19 |
| -263 | 19 |
| -256 | 17 |
| -258 | 17 |

## Reuse gaps

| gap_accesses | count |
|---|---|
| 2 | 440 |
| 122 | 48 |

## Most accessed regions

| region_number | count |
|---|---|
| 1 | 256 |
| 2 | 256 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
