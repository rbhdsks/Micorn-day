# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 512 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 64 |
| touched_line_footprint_bytes | 1024 |
| minimum_byte_address | 131072 |
| maximum_byte_address | 132092 |
| adjacent_same_line_accesses | 384 |
| adjacent_same_line_fraction | 0.7514677103718199 |
| accesses_to_previously_seen_line | 448 |
| mean_reuse_gap_accesses | 9.571428571428571 |

## Most accessed lines

| line_number | count |
|---|---|
| 8192 | 8 |
| 8193 | 8 |
| 8194 | 8 |
| 8195 | 8 |
| 8196 | 8 |
| 8197 | 8 |
| 8198 | 8 |
| 8199 | 8 |
| 8200 | 8 |
| 8201 | 8 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 0 | 384 |
| 1 | 123 |
| -15 | 4 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 1 | 123 |
| -15 | 4 |

## Reuse gaps

| gap_accesses | count |
|---|---|
| 1 | 384 |
| 61 | 64 |

## Most accessed regions

| region_number | count |
|---|---|
| 32 | 512 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
