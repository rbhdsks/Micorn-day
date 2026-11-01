# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 512 |
| line_size_bytes | 16 |
| region_size_bytes | 4096 |
| unique_cache_lines | 457 |
| touched_line_footprint_bytes | 7312 |
| minimum_byte_address | 262208 |
| maximum_byte_address | 294784 |
| adjacent_same_line_accesses | 0 |
| adjacent_same_line_fraction | 0.0 |
| accesses_to_previously_seen_line | 55 |
| mean_reuse_gap_accesses | 130.36363636363637 |

## Most accessed lines

| line_number | count |
|---|---|
| 17733 | 3 |
| 16897 | 3 |
| 16534 | 3 |
| 17417 | 3 |
| 16526 | 3 |
| 17655 | 3 |
| 16457 | 3 |
| 16756 | 2 |
| 16590 | 2 |
| 17133 | 2 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| -67 | 3 |
| -211 | 3 |
| 691 | 2 |
| 224 | 2 |
| 186 | 2 |
| -1166 | 2 |
| -208 | 2 |
| 20 | 2 |
| 181 | 2 |
| -306 | 2 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| -67 | 3 |
| -211 | 3 |
| 691 | 2 |
| 224 | 2 |
| 186 | 2 |
| -1166 | 2 |
| -208 | 2 |
| 20 | 2 |
| 181 | 2 |
| -306 | 2 |

## Reuse gaps

| gap_accesses | count |
|---|---|
| 27 | 2 |
| 114 | 2 |
| 4 | 2 |
| 13 | 1 |
| 45 | 1 |
| 79 | 1 |
| 5 | 1 |
| 90 | 1 |
| 59 | 1 |
| 14 | 1 |

## Most accessed regions

| region_number | count |
|---|---|
| 66 | 85 |
| 71 | 71 |
| 70 | 70 |
| 64 | 65 |
| 69 | 62 |
| 68 | 58 |
| 65 | 52 |
| 67 | 49 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
