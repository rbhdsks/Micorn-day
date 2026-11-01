# Trace analysis

| Measurement | Value |
|---|---|
| accesses | 33280 |
| line_size_bytes | 64 |
| region_size_bytes | 4096 |
| unique_cache_lines | 80 |
| touched_line_footprint_bytes | 5120 |
| minimum_byte_address | 4096 |
| maximum_byte_address | 14332 |
| adjacent_same_line_accesses | 8672 |
| adjacent_same_line_fraction | 0.26058475314763063 |
| accesses_to_previously_seen_line | 33200 |
| mean_reuse_gap_accesses | 47.65397590361446 |

## Most accessed lines

| line_number | count |
|---|---|
| 192 | 528 |
| 193 | 528 |
| 194 | 528 |
| 195 | 528 |
| 196 | 528 |
| 197 | 528 |
| 198 | 528 |
| 199 | 528 |
| 200 | 528 |
| 201 | 528 |

## Consecutive line deltas

| delta_lines | count |
|---|---|
| 0 | 8672 |
| 64 | 768 |
| 66 | 736 |
| 62 | 704 |
| 68 | 704 |
| 70 | 672 |
| 60 | 640 |
| 72 | 640 |
| 74 | 608 |
| 58 | 576 |

## Line transitions (zero deltas excluded)

| delta_lines | count |
|---|---|
| 64 | 768 |
| 66 | 736 |
| 62 | 704 |
| 68 | 704 |
| 70 | 672 |
| 60 | 640 |
| 72 | 640 |
| 74 | 608 |
| 58 | 576 |
| 76 | 576 |

## Reuse gaps

| gap_accesses | count |
|---|---|
| 4 | 15856 |
| 1 | 8672 |
| 3 | 7680 |
| 67 | 480 |
| 1988 | 480 |
| 499 | 1 |
| 547 | 1 |
| 2515 | 1 |
| 2563 | 1 |
| 4531 | 1 |

## Most accessed regions

| region_number | count |
|---|---|
| 3 | 16896 |
| 1 | 8192 |
| 2 | 8192 |

## Interpretation limits

Each row is one address observation mapped to its starting cache line. Request sizes and read/write/PC metadata are not interpreted. Footprint is unique touched lines, not required cache capacity. Reuse gap is access-index distance, not distinct-line reuse distance. Delta counts describe transitions, not prediction accuracy. No hit rate or speedup is inferred.
