# Trace contract and provenance

The runner generates trace data into `build/benchmarks/traces/`; committed source
formulas are in `../scripts/generate_traces.py`. Each replay CSV has exactly:

```csv
address,gap
0x00001000,20
0x00001010,20
```

Addresses require explicit `0x` hexadecimal, a 32-bit range and four-byte
alignment. Gap is a nonnegative decimal integer in 0..100000. There are 1..65536
rows. Each row is a naturally aligned, immutable 32-bit read, not a load/store
instruction or a timestamp. The `.mem` encoding packs address[63:32] and gap[31:0].

The 13 generated scenarios are:

| Trace | Purpose |
|---|---|
| zero_gap_stream | Sequential lines without intentional compute gap |
| tensor_stream | Four words per line, six-cycle spacing |
| column_stride | Fixed +64-byte stride |
| tiled_reuse | Reuse inside successive small tiles |
| embedding_gather | Irregular uniform line choices, seed 20261101 |
| interleaved_conflicting | Two streams with corresponding default cache indices equal |
| phase_shift | Sequential-to-64-byte-stride change |
| pollution_return | 64 repetitions of 0x1000, 0x13d0, 0x13e0, 0x13f0, 0x1000 |
| three_line_bursts | 64 disjoint three-line bursts; prediction arrives as each burst ends |
| two_stream_disjoint_sets | Independent +32-byte streams using even/odd cache indices |
| same_line | Four words in one line, repeated; empty inter-line stride histogram |
| modelled_matmul_ijk_ab_reads | Filtered immutable A/B reads from Level 1 ijk algorithm |
| modelled_matmul_ikj_ab_reads | Same filter and dimensions, ikj loop order |

The modelled dimensions are M=4, K=8, N=8 and four-byte row-major elements.
Full logical source traces and numeric-reference checks remain in generated
`modelled_sources/`. Filtering preserves original A/B read order, excludes all
C accesses/writes/initialisation, and assigns six replay gap cycles as an explicit
assumption. The manifest records source and filtered SHA256s, loop order, counts,
filter and limitations. These are algorithm-access models, not real machine
traces. Their values are not the RTL memory data contents.

For a custom strict read-only trace directory, use `--trace-dir PATH`. Optional
`manifest.json` entries use `name`, `file=name.csv`, `kind`, `provenance`, and
optionally `rows` and `sha256` (validated when present). Use safe names containing
letters, digits, underscores or hyphens. Absent provenance is never inferred to
be a real application capture. Preserve raw inputs and describe any filtering,
address remapping and timing assumptions before drawing workload conclusions.
