# Level 1 — memory trace analysis

Status: Nitesh’s reproducible analysis and modelled matrix-multiplication experiment are integrated into Phase 1. An official or captured workload trace remains unavailable; no captured-workload conclusions are claimed.

## Run

Python 3.10 or newer; no external dependencies. Run from the `Phase1/` directory (`cd Phase1` from the repository root):

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

## Matrix-multiplication notebook (start here)

From `Phase1/`, open `level1/matmul_analysis.ipynb` in VS Code with the Jupyter extension, or use JupyterLab. Archived numerical and graph outputs from the upstream execution are included; the relocated setup cell has been cleared so its path is resolved on your machine.

For an isolated local environment, run from `Phase1/`:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r level1/requirements.txt
python -m jupyterlab level1/matmul_analysis.ipynb
```

Select the environment's Python kernel and choose **Run All**. No model weights, external dataset, or GPU is required. Change `CONFIG` and `LINE_SIZE` near the top to explore other dimensions. Rerunning overwrites `level1/results/modelled_matmul/`, so copy results elsewhere if you want to preserve an experiment.

The notebook:

1. Generates deterministic matrices and executes two scalar loop orders (`ijk`, `ikj`).
2. Records logical A/B/C accesses and checks numerical results against a dot-product reference.
3. Analyses the combined trace and compute-read streams separately.
4. Plots per-operand access patterns, B-address strides, and cache-line reuse gaps.
5. Compares grouping at 32-, 64-, and 128-byte line sizes.
6. Saves raw CSVs, metadata, numerical results, summaries, figures, and `analysis.md`.

### Generate without Jupyter

```sh
python3 level1/generate_matmul_trace.py --m 16 --k 16 --n 32 --order ijk --output level1/results/modelled_matmul/ijk
python3 level1/generate_matmul_trace.py --m 16 --k 16 --n 32 --order ikj --output level1/results/modelled_matmul/ikj
python3 level1/analyze_trace.py level1/results/modelled_matmul/ijk/trace.csv --format csv --output level1/results/modelled_matmul/ijk
```

These are **modelled algorithm-access traces**, not captured machine instructions. Arrays are row-major four-byte integer elements in separate assigned address regions. Each multiply-accumulate explicitly logs A-read, B-read, C-read, C-write; no register reuse or A-load hoisting is assumed. C initialisation is a separate logged phase; constructing A/B is excluded. Both orders use the same policy and operation counts. `sequence` is not cycles. The Python objects' actual addresses and execution overhead are not traced.

The CSV includes `phase`, `operation`, `operand`, access size, and loop indices for notebook filtering. The generic CLI still analyses only `address` and does not distinguish reads/writes. No request crosses a 64-byte line in this model because elements are four-byte aligned. No performance or real-AI-workload claim follows from these traces alone. Official acceptance remains to be confirmed.

## Phase 1 integration and provenance

Imported with history from `nitesh/feat-level1`, commit
`e0ab37c30e7a02dd1f3d868aef956ee88104a8b0`. The analyser, scalar
matrix generator, raw modelled traces and numerical results retain their
original meaning. The directory was relocated to `Phase1/level1/`; machine-local
paths in archived display output were removed or made relative. Python bytecode
is excluded from the submission. The notebook locates its inputs when launched
from the repository root, `Phase1/`, or `Phase1/level1/`.

The notebook's archived analysis uses **64-byte lines**. Phase 1 RTL uses
**16-byte lines**, a declared baseline choice described in
[the cache specification](../level2/cache_specification.md). Level 5 re-analyses
its replay inputs with 16-byte lines; do not copy the notebook's 64-byte counts
into an RTL hit-rate claim.

The full modelled matrix trace includes mutable C reads/writes and cannot be
replayed faithfully through this read-only cache. The Level 5 adapter uses
compute-phase **A/B reads only**, preserving address order and recording the
excluded operations. That is an immutable-input access study, not full matrix
execution timing. See [Level 5](../level5/README.md).

To regenerate the original synthetic analysis without overwriting archived results:

```sh
python3 level1/analyze_trace.py level1/examples/synthetic_sequential.txt \
  --format text --line-size 16 --output build/level1/synthetic_16B
```

The standard-library CLI and unit tests do not require the notebook packages.
