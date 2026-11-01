# Level 5: paired evaluation and validation-first policy selection

This evaluation measures seven hardware configurations on identical immutable demand streams. [The evaluation plan](evaluation_plan.md) defines the selection rule and formulas before held-out execution. The runner seals a validation-only `selection.json` before issuing any held-out commands and verifies that its hash stays unchanged afterward.

```sh
# From repository root; Icarus Verilog/VVP and Python3.10+ required.
python3 Phase2/level1/fetch_corpus.py --download
python3 Phase2/level5/scripts/run_benchmarks.py
PYTHONPATH=Phase2/level5/scripts python3 -m unittest discover -s Phase2/level5/tests -v
```

The full suite has 385 primary runs (55 cases × seven variants), plus 20 validation-only probe-interval sensitivity runs. Output goes to `Phase2/build/benchmarks/`. Source corpus and raw per-request samples remain ignored. Core synthetic/numeric tests require no downloaded data; `--no-corpus` is a separately labelled 49-case subset.

| Variant | Data capacity | Prediction/control |
|---|---|---|
| none | 1 KiB | Phase 1 cache, no speculation |
| next_line | 1 KiB | Phase 1 next-line prediction |
| stride | 1 KiB | Phase 1 global stride prediction |
| victim_buffer | 1 KiB + 32 B | Two demand-victim entries; speculation disabled |
| global_buffer | 1 KiB + 32 B | Global stride, two speculative entries |
| region_buffer | 1 KiB + 32 B | Four 4 KiB address-region histories, two speculative entries |
| context_feedback | 1 KiB + 32 B | Region histories plus global mature-outcome gating/recovery |

The victim control has the same extra **data bits**, not equal area, comparators, metadata, timing or energy. Additional buffering itself can explain a gain. Region histories distinguish address contexts; the usefulness gate is global and is not per-region learned quality or semantic tensor awareness.

## Evidence files

The retained result package uses `summary.csv`, `aggregates.csv`, `selection.json`, `evaluation.json`, `predeclared_plan.json`, `provenance.json` and a trace manifest. Per-run RTL CSVs/logs retain original counters. Per-request samples reconcile exactly with aggregate latency sums and maxima and support empirical nearest-rank p50/p95 latency. The baseline adapter is checked against all 39 original Phase 1 reference results before publication.

`hits` counts main-cache hits at demand acceptance. `buffer_hits` is separate, and `service_hit_rate=(hits+buffer_hits)/accesses`. A victim hit is not a prefetch hit. For speculative variants, `timely_useful=buffer_hits`; in victim mode, timely/late prefetch counters stay zero. `issued=timely+late+unused_evicted+resident_unconsumed` must conserve after natural quiescence.

## First-pass audit findings

The earlier package was a useful verified baseline, but its scientific breadth was limited: one fixed irregular seed, mostly diagnostic patterns, no genuine semantic context signal, global history interference, speculative main-cache eviction, one outstanding memory transaction and no measured area/timing/energy. Accurate predictions could be late; useful guesses could still increase traffic. A polished slide deck did not resolve these limitations.

The upgrade adds falsifiable address-context and outcome mechanisms, stronger input provenance, complete numeric microkernels, a same-extra-data victim control, declared held-out conditions and explicit rejection/selection criteria. It retains serial-driver, small-cache, read-only and deterministic-memory limits. Any company-facing claim must be a measured subsystem tradeoff rather than a promised DDR/HBM or application throughput result.
