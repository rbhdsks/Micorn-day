# Source and evidence provenance

## Source history

Phase 1 is based on `rbhdsks/Micorn-day`, branch `nitesh/feat-level1`, commit `e0ab37c30e7a02dd1f3d868aef956ee88104a8b0`. The new `phase-1` branch retains that ancestry. The original `level1/` directory was moved into `Phase1/level1/`; raw modelled matrix traces and numerical outputs remain available. Path/discovery instructions are adapted to the new layout. Committed Python bytecode is removed.

The starting cache, stride predictor, memory model and original cache/stress/predictor tests come from the user's supplied `ai_cache_project` baseline, audited before this build. They are integrated under `level4/` with explicit changes: next-line RTL comparison, portable output paths, bounded trace draining and timing/outcome instrumentation. Phase 1 retains its direct-mapped speculative insertion behavior, including known pollution limitations; the separate prefetch buffer and feedback are Phase 2 work.

The initial repository plan is retained at [initial_plan.md](initial_plan.md) as historical context. Its pending checklist predates this integrated build. The current status is the [Phase 1 README](../README.md) and [release evidence](RELEASE.md). Recommendations in the plan are not additional organizer requirements.

## Requirements used

The user's current build request, pasted design-thinking explanation and supplied screenshots define this phase's requested deliverables. Level 2 requires an architecture/specification and rationale; Level 3 requires algorithm/state/pseudocode plus help/failure cases and scheduling decisions; Level 5 requires precise demand hit rate and completion-cycle speedup.

Original organizer slides and official acceptance rules are not independently verified here. No official scores or winning probabilities are asserted. The supplied academic PDF informs the separate CDM research chapter; that private source PDF and the chat screenshots are not copied into the Git repository.

## Trace classes

| Class | Source | Meaning and limit |
|---|---|---|
| Imported Level 1 examples | Nitesh's feature branch | Parser checks and explicitly modelled scalar matrix access order |
| Synthetic RTL probes | Deterministic generators in Level 5 | Regular, irregular, conflict, burst and pollution diagnostic patterns |
| Modelled A/B replay | Level 1 generator with explicit filtering | Immutable input-operand read subset; excludes initialization, writes and mutable C |

A logical trace sequence is not a hardware timestamp. Matrix results are checked by the Level 1 generator, but the RTL returns its independent deterministic backing-memory values; it does not execute matrix arithmetic. Comparing the address replay does not measure inference execution time.

The Level 5 run records source hashes, input hashes, filter/count provenance, geometry, memory latency, policies, command results and tool versions. Local absolute paths must not be required to reproduce committed reference evidence.

## Authorship and assistance

The inherited history records AI assistance in Level 1. Phase 1 integration, RTL comparison logic, tests, research arithmetic, figures, report and presentation also used AI assistance. Team members should review and understand the design, keep their own experiment/change records and follow the organizer's disclosure rules. No independent authorship or algorithmic novelty certification is claimed.
