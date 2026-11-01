# Final context aware cache evaluation

Read the [final presentation and report](../Final/README.md), inspect the [18-figure gallery](plots/README.md), or start with a challenge level:

| Level | Evidence |
|---|---|
|1|[Checked datasets and split policy](level1/README.md)|
|2|[Architecture and storage](level2/README.md)|
|3|[Regional algorithm and control](level3/README.md)|
|4|[RTL, FSM, simulation and FPGA flow](level4/README.md)|
|5|[Matched benchmarks](level5/README.md)|

```sh
make -C Phase2 test
make -C Phase2 independent
make -C Phase2 benchmark
make -C Phase2 figures
```

Python3.10+, Icarus/VVP and GNU Make run the core. Independent lint/assertions additionally require Verilator and a C++ compiler; synthesis requires Yosys; figures use GNU Octave and gnuplot or native MATLAB. Source fetching is explicit and checksum-locked. Core tests do not require corpus downloads.

Regional history repairs the separated-stream diagnostic; the buffer repairs speculative main-cache pollution. The victim control outperforms region on held-out aggregate time and traffic. Feedback ties region-only on validation/holdout and remains optional. The evidence establishes conditional mechanisms, not universal superiority, full inference acceleration or a competition outcome.

[First audit](audit/research_first_pass.md), [second RTL audit](audit/rtl_second_pass.md), [independent arithmetic audit](audit/results_second_pass.json), [mathematical contract](docs/MATH_AND_CONTEXT.md), [primary research](research/literature_review.md) and [MATLAB runtime disclosure](matlab/README.md) support the claims.
