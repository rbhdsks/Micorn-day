# Micron cache and prefetch project

Phase 1 is the reproducible baseline: trace analysis, a justified cache specification, explicit prefetch algorithms, functional SystemVerilog, and measured three-policy comparisons. The next upgrade will live on a separate Phase 2 branch derived from this baseline.

Start with **[Phase 1](Phase1/README.md)**. Run from this repository root:

```sh
make all
make synth       # optional additional tool: Yosys
```

The core needs Python 3.10+, GNU Make, Icarus Verilog and VVP. The analysis CLI and benchmark runner use the Python standard library; Jupyter/plotting dependencies are optional.

| Folder | Deliverable |
|---|---|
| [Phase1/level1](Phase1/level1/README.md) | Nitesh's imported trace analyser, modelled matrix-multiplication generator, notebook and evidence |
| [Phase1/level2](Phase1/level2/cache_specification.md) | Cache specification, block diagram and reasons for the architecture |
| [Phase1/level3](Phase1/level3/prefetch_strategy.md) | Trigger, distance, degree, confidence, filtering, priority, insertion, state and pseudocode |
| [Phase1/level4](Phase1/level4/README.md) | Cache/prefetch RTL, memory model, testbenches and generic synthesis script |
| [Phase1/level5](Phase1/level5/README.md) | Reproducible no-prefetch / next-line / stride RTL performance comparisons |
| [Phase1/docs](Phase1/docs/PROVENANCE.md) | Provenance, integration contract, verification and Phase 2 plan |

`phase-1` inherits `nitesh/feat-level1` commit `e0ab37c30e7a02dd1f3d868aef956ee88104a8b0`. Its history and modelled data are retained. Python bytecode and local build products are excluded. See [source provenance](Phase1/docs/PROVENANCE.md).

These are modelled/synthetic access experiments and simulated memory timing. They are not measured AI application acceleration, a neural predictor, physical DRAM validation or an FPGA implementation. The [Phase 2 roadmap](Phase1/docs/PHASE2_ROADMAP.md) keeps proposed enhancements separate from Phase 1 results.
