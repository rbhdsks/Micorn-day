# MATLAB figure source

Open MATLAB R2020a or later, add this directory to the path and run:

```matlab
generate_figures
```

The function reads the retained benchmark CSV and 16-byte-line trace-analysis JSON files using paths relative to its own location. It checks demand hit rate (`hits / accesses`), completion speedup (`baseline completion cycles / policy completion cycles`) and prefetch-fate conservation before plotting. It writes nine figure families, each as PNG and vector PDF, under `Phase1/build/matlab_figures/`:

| Family | Evidence and meaning |
|---|---|
| `01_speedup` | Next-line/stride completion speedup across all 13 workloads |
| `02_hit_rate` | Demand hit fraction for all three policies |
| `03_latency` | Mean accepted-demand to response-availability cycles |
| `04_traffic` | DRAM transaction ratio to no prefetch; pollution shown separately |
| `05_prefetch_fates` | Timely, late, unused-evicted and resident stride prefetches |
| `06_pollution` | Absolute completion cycles and DRAM transactions for hot-line pollution |
| `07_workload_footprint` | Distinct touched 16-byte lines; this is not a capacity requirement |
| `08_cdm_probabilities` | Recalculated supplied initial-factor choice probabilities |
| `09_cdm_storage` | Analytical float64 parameter-only storage: full `n^2` versus factors `2nr` |

The function also writes the measured benchmark table and separately labelled CDM initial-factor NLL, probability and storage tables as CSV. It uses a shifted softmax and excludes self-interactions in the six-observation CDM illustration. These calculations are separate from the RTL experiments. They do not train a model or measure total process memory.

MATLAB was unavailable in the authoring environment, so this source has **not been executed in MATLAB**. The published PNG/PDF/SVG figures under [plots](../plots/README.md) were generated and inspected using the Python plotting script from the same source measurements. They are not presented as MATLAB runtime output. This MATLAB source covers the same nine evidence families; renderer-specific layout may differ.
