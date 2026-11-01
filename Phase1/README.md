# Phase 1: complete baseline

This phase connects the five challenge levels in one reproducible package. The current foundation is on main. [Open the presentation](presentation/phase1_presentation.pptx), [technical report](report/phase1_report.pdf) or [figure gallery](level5/plots/README.md). It preserves Nitesh's Level 1 work and implements a small, data-checking read-only memory subsystem for policy evaluation.

## Run end to end

From the repository root:

```sh
make all
```

Or from this directory:

```sh
make test        # Level 1, benchmark tooling and RTL correctness
make benchmark   # traces -> all three RTL modes -> measured report
make synth      # requires Yosys; generic synthesis, no physical sign-off
```

On Ubuntu/Debian install `python3 make iverilog` and optionally `yosys`. On macOS install the same tools with your package manager. No Python packages are needed for the CLI path. Optional notebook dependencies are in `level1/requirements.txt`.

Tool overrides are explicit:

```sh
make test IVERILOG=/path/to/iverilog VVP=/path/to/vvp
make synth YOSYS=/path/to/yosys
```

## Filing system

```text
Phase1/
  level1/   imported analysis, modelled-data generator, notebook, tests, results
  level2/   cache specification and architecture diagram
  level3/   predictor algorithms, state, scheduling and limitations
  level4/
    rtl/    synthesizable hardware only
    tb/     simulation models and self-checking testbenches
    synth/  generic synthesis script
  level5/
    scripts/ pipeline and metric/report generation
    tests/   trace/report/provenance regression tests
    results/reference/ compact measured evidence committed for review
  docs/     integration, provenance, verification, release and Phase 2 roadmap
  tools/    verification/evidence orchestration
  build/    generated binaries, traces, logs and reports; ignored by Git
```

The original imported Level 1 evidence remains under `level1/results/`. Newly executed experiments go under `build/`; `make clean` removes only that generated directory. `make reference` deliberately exports compact benchmark evidence after a successful run.

## Level deliverables

1. [Trace analysis](level1/README.md): parsing, locality/stride/reuse measurements, modelled matrix multiplication, explicit provenance.
2. [Cache specification](level2/cache_specification.md): capacity, line size, mapping, replacement, write scope, request handling, insertion and a block diagram.
3. [Prefetch strategy](level3/prefetch_strategy.md): algorithms and bounded state with all scheduling decisions and expected failure modes.
4. [RTL and verification](level4/README.md): functional cache, stride and next-line reference predictors, deterministic memory model and data/protocol checks.
5. [Performance validation](level5/README.md): identical traces/cache/memory for no prefetch, next-line and stride; demand hit rate, completion-cycle speedup, latency, outcomes and traffic.

## Baseline scope

- 1 KiB data cache, 64 direct-mapped 16-byte lines, 32-bit aligned read requests.
- One queued demand and one memory transaction outstanding; ready/valid interfaces.
- Read-only immutable memory; no writes, coherence, virtual memory or bus errors.
- Single global signed-stride predictor; next-line RTL provides a timed reference.
- Modelled A/B matrix reads are filtered from Level 1; mutable C traffic is excluded.
- No buffer, usefulness feedback, multiple trackers or adaptive distance in Phase 1.

[Integration contract](docs/INTEGRATION.md), [verification](docs/VERIFICATION.md), [provenance](docs/PROVENANCE.md), [measured reference](level5/results/reference/report.md), and [release evidence](docs/RELEASE.md) document the exact limits.

Demand hit rate is **demand hits / accepted demand accesses**. Speedup is **no-prefetch completion cycles / policy completion cycles**. Prefetch activity never increases the demand-access denominator. Completion and final quiescence are separate measurements. Simulation cycles do not establish real application or physical memory speedup.

## Phase 2 boundary

Phase 2 will branch from the completed Phase 1 commit. Its proposed first upgrade is a small separate prefetch buffer, followed by bounded consumption/waste admission feedback. It must be measured against this baseline with the same conditions. See [the roadmap](docs/PHASE2_ROADMAP.md). Phase 2 work has not been implemented on this branch.

## Executed starting notebooks and publication material

- [Level 2 cache model](level2/cache_architecture.ipynb)
- [Level 3 predictor state](level3/prefetch_walkthrough.ipynb)
- [Level 4 RTL verification](level4/rtl_walkthrough.ipynb)
- [Level 5 measured results](level5/results_walkthrough.ipynb)
- [Separate CDM arithmetic](research/cdm/cdm_walkthrough.ipynb)

`make notebooks` executes these standard-Python cells and retains real outputs. The original Level 1 notebook remains available separately. `make all` now also tests the Level 2 cache model, Level 3 predictor model and CDM arithmetic.

To regenerate scientific plots:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-figures.txt
make figures PYTHON=.venv/bin/python
```

The [MATLAB scripts](level5/matlab/README.md) read the same measurements. MATLAB was unavailable during authoring. The [16-page report](report/README.md) contains native editable equations and the [23-slide PowerPoint](presentation/README.md) contains editable data charts/tables. The low-rank CDM chapter is research, not a new hardware performance claim.
