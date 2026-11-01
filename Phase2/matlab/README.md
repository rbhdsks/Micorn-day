# MATLAB compatible scientific analysis

`generate_deep_analysis.m` consumes transparent numeric matrices prepared from the exact measured CSV, with row/column definitions and source hash in `analysis/data/manifest.json`. It validates speedup, traffic ratios and prefetch fate conservation before plotting. No toolbox-specific statistics functions or trained models are needed.

```sh
# Repository root, after reproducing or retaining benchmark evidence
python3 Phase2/analysis/prepare_data.py
# In MATLAB:
# addpath('Phase2/matlab'); generate_deep_analysis
# Executed alternative on this host:
octave-cli --quiet --eval "addpath('Phase2/matlab'); generate_deep_analysis;"
```

The 18 figure families and their calculations were executed using GNU Octave 11.3.0 with gnuplot 6.0.6. Native MATLAB is unavailable, so native MATLAB compatibility remains unverified. The script uses base MATLAB operations. Its Octave-only graphics selection is guarded by `OCTAVE_VERSION` and does not run in MATLAB. Explicit plotted keys avoid an Octave toolkit export issue with automatic legends. The final FSM figure uses `python3 Phase2/analysis/render_fsm_fallback.py` (Matplotlib) on identical retained signal samples because a later multi-axis export stalled. This renderer changes presentation, not the measured samples or calculated metrics.

All28 validation/held-out aggregate values agree with separately computed Python metrics within1e-12. The matrices preserve the complete55-by7 primary comparison. Per-case p95 means the nearest-rank percentile of request latencies in that replay. The transaction-cost curve is an analytical preference `J=C+lambda*D`, not an energy or physical DRAM simulation.

The [gallery](../plots/README.md) links every result, scope and corresponding source. Full-size vector PDFs support detailed inspection of dense heatmaps.
