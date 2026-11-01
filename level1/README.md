# Level 1 — memory trace analysis

Status: initial tooling is ready; actual workload analysis awaits a real trace and its specification. No real workload conclusions have been made.

## Run

Python 3.10 or newer; no external dependencies. Run from the project root:

```sh
python3 level1/analyze_trace.py level1/examples/synthetic_sequential.txt --format text --output level1/results/synthetic_sequential
PYTHONPATH=level1 python3 -m unittest discover -s level1/tests -v
```

For a real trace:

```sh
python3 level1/analyze_trace.py /absolute/path/to/trace.csv --format csv --line-size 64 --output level1/results/workload_name
```

64 bytes is a configurable analysis assumption, not an official cache specification. Repeat with other line sizes when useful.

## Supported initial formats

- Text: one nonnegative byte address per line. Blank lines and `#` comments are allowed.
- CSV: a header with an exact `address` column; one nonnegative byte address per row. Additional columns are currently ignored, not analysed.
- Numbers are decimal unless prefixed with `0x`/`0X`. Bare hexadecimal is intentionally rejected; verify the actual trace format before converting.
- Each row is one observation at its starting line. Multi-line request sizes, read/write filtering, timestamps, instruction addresses, and interleaved stream separation are not yet modelled. Do not use this initial parser unchanged if those distinctions are necessary for the supplied trace.

## Outputs and definitions

`summary.json` contains machine-readable counts and top-ten histograms. `report.md` presents the same measurements.

- Line number = byte address // line size.
- Touched-line footprint = unique line count × line size, not minimum cache capacity.
- Line delta = current line number minus previous line number. Nonzero deltas exclude adjacent observations in the same line; they do not remove stream resets or interleaving.
- Reuse gap = number of access-index steps since the previous observation of that line. Immediate reuse has gap 1. This is not distinct-line reuse distance or a cache hit measurement.
- Region number = byte address // region size (default 4096 bytes). These are coarse buckets, not identified model tensors or allocations.
- The implementation streams the input, but exact counters retain unique lines, regions, deltas, and reuse gaps in memory. Very large traces may need bounded-memory alternatives.

No cache hit rate, prefetch accuracy, or speedup is estimated here. Those require cache/predictor/timing models. Synthetic examples are parser and statistics checks only.

## Next steps with the real trace

1. Record provenance and format in `workload_analysis.md`.
2. Adapt the parser to the documented schema, preserving metadata needed for analysis.
3. Run whole-trace analysis and inspect representative windows for phase changes.
4. Compare line sizes and distinguish within-line locality from line-to-line strides.
5. Explain observed patterns and exceptions with counts and suitable plots.
6. Recommend candidate predictors; defer performance claims until baseline modelling.
