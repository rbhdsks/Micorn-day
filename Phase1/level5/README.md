# Level 5: measured performance validation

Run from `Phase1/`:

```sh
python3 level5/scripts/run_benchmarks.py --output build/benchmarks
python3 -m unittest discover -s level5/tests -v
```

The first command generates and analyses 13 deterministic read traces, compiles
both RTL candidate policies and runs every trace in **none / next_line / stride**
modes. Geometry, memory model and driver rules are identical. Every response is
data-checked. No Python immediate-fill result is substituted for RTL timing.
The CLI uses only the Python standard library, Icarus Verilog and VVP.
`IVERILOG`, `VVP` and `IVFLAGS` environment overrides use shell-style argument
splitting, without a shell invocation. Simulator replay/output paths must not
contain whitespace because the RTL reads string plusargs with `%s`. Use the explicit CLI options for geometry
and latency.

```sh
python3 level5/scripts/run_benchmarks.py --output build/latency128 --latency 128 --workload column_stride
python3 level5/scripts/run_benchmarks.py --output build/small_cache --index-bits 4
```

## Read the measured result first

Open [the executed results notebook](results_walkthrough.ipynb), [the complete measured report](results/reference/report.md) or [the figure gallery](plots/README.md). The following completion cycles come directly from the retained RTL CSV.

| Workload | No prefetch | Next-line | Stride | Why it matters |
|---|---:|---:|---:|---|
| Column stride | 21,098 | 21,098 | 12,573 | Stride recognizes the line pitch |
| Hot-line pollution | 7,888 | 8,895 | 8,927 | Speculation evicts demanded data |
| Modelled ijk A/B | 6,940 | 7,154 | 6,940 | Global stride sees no gain |
| Modelled ikj A/B | 6,404 | 6,443 | 6,404 | Extra hits do not guarantee faster completion |

The [MATLAB source](matlab/README.md) and [Python plot source](scripts/plot_results.py) use the same evidence. CDM figures form a separate research illustration and do not appear as a fourth RTL benchmark policy.


## Files and generated evidence

- `scripts/trace_io.py`: strict aligned-read trace parser and packed `.mem` writer.
- `scripts/generate_traces.py`: synthetic probes and a bridge to Nitesh's Level 1
  generator, preserving only immutable A/B compute reads.
- `scripts/run_benchmarks.py`: compilation, RTL replay, same-geometry Level 1
  analysis, configuration checks and provenance.
- `scripts/metrics.py`: counter validation, CSV metrics and data-derived report.
- `tests/`: parser, filtering/provenance and measurement/report regressions.
- `traces/README.md`: trace contract and scenario descriptions.
- `results/reference/`: curated measured snapshot, when exported by the project
  reproduction workflow. Regenerated evidence goes under ignored `build/`.

Generated output includes `summary.csv`, `report.md`, `provenance.json`, raw
`runs/*.csv` and `runs/*.log`, 16-byte-line `analysis/` reports, packed `replay/`
inputs and `traces/manifest.json`. Source/tool versions and SHA256s identify the
experiment. Filenames and commands use paths relative to `Phase1/` by default.
Starting a new run invalidates old summary/report/provenance files; a failed run
cannot be exported as a current successful measurement. Raw attempt logs remain
available for diagnosis. Export only when a fresh provenance file confirms success.

## Metric contract

Demand hit rate = demand hits / total demand accesses.

Speedup = no-prefetch demand completion cycles / policy demand completion cycles.

`completion_cycles` ends at the last consumed demand response; the final unused
compute gap is excluded. `quiescent_cycles` adds bounded natural draining of the
predictor candidate pipeline, candidate slot and memory controller. There is no
fixed 100-cycle pad. Both cycle definitions and speedup ratios are published.
This explicitly differs from the older audited package's padded cycle counts.

Accepted-to-response latency excludes request waiting before acceptance and
consumer stalls after data becomes available. Offer-to-response also includes
preaccept request waiting. Total completion cycles include the prescribed
consumer stalls and all earlier compute gaps.

Consumed-prefetch accuracy = (timely + late first consumption) / issued reads.
A zero denominator is N/A. Outcome conservation at quiescence is checked:
issued = timely + late + unused evicted + resident unconsumed. Still-resident
lines are unresolved; an unused eviction alone does not prove demand pollution.
Traffic counts demand and speculative transactions, each 16 bytes in this model.

## Scope and limitations

The replay driver is serial and adds each trace's compute gap after consuming its
response. Zero gap is not a full-rate CPU. The memory model is not a vendor DRAM
model. Synthetic patterns are directed tests. Filtered modelled matmul traces are
not captured instructions, complete inference or application execution timing.
The trace generator checks numeric matmul correctness separately; RTL replay
returns address-derived reference words rather than matrix numeric values.

The current direct-mapped prefetch insertion may evict useful demand data; the
pollution and burst workloads intentionally expose regressions. A global stride
predictor can fail on interleaved streams. No universal performance improvement,
physical bandwidth reduction or real-AI speedup is claimed. Phase 2 can compare
buffer isolation and usefulness feedback against this reproducible baseline.
