# Phase 2: upgrade plan, not Phase 1 implementation

Create a separate branch from the final verified Phase 1 commit when Phase 2 begins. Keep `phase-1` available as the reproducible baseline; record its exact commit in the Phase 2 report. No Phase 2 branch or enhanced results are implied by this document.

## First checkpoint: isolate speculative data

Add a one- or two-entry fully associative prefetch buffer. Speculative fills enter that buffer, not the demand cache. Promote a line into the demand cache only when a demand consumes it. Recheck queued demands against both cache and buffer. Filter duplicates in cache, buffer and selected/in-flight transaction. Preserve valid/data stability, ordered responses and shared reset.

A two-entry buffer has approximately `2 * (128 data + 28 identity + 1 valid) = 314` logical storage bits before control. Comparators/muxes can affect timing. Synthesize before claiming cheap hardware. This is an established stream-buffer technique; the contribution is a verified integration and measured tradeoff, not invention of prefetch buffering.

Test the Phase 1 `pollution_return` and conflict cases first. Distinguish main-cache hits, timely buffer hits and late consumption; do not silently change demand hit-rate definitions.

## Second checkpoint: bounded usefulness feedback

Use mature outcomes: consumption is useful, unused buffer replacement is waste, still-resident lines are unresolved. Small saturating counters can gate new speculation after persistently low usefulness. Continue learning during suppression and allow bounded probes/cooldown so a useful phase can recover.

Test short bursts, regular/irregular/regular transitions, counter limits, simultaneous queue events and recovery. Choose thresholds with a declared sweep and validate on held-out patterns/seeds. Current Phase 1 already issues no predictions on some irregular traces, so feedback cannot be promised to improve every workload.

## Optional third checkpoint

Add a bounded region-indexed stride table if stream interference remains important. Genuine PC/stream indexing requires a new input and authentic trace metadata. More trackers alone do not cure direct-map conflicts. Adaptive distance and multiple outstanding transactions should be separate projects after correctness and evidence gates.

## Comparison gates

Use the same main cache, memory model, traces, seeds and timing. Ablate original stride, buffer-only and buffer+feedback. Report added storage and target synthesis cost separately. Keep no-PF and next-line references. Show completion cycles, offered/accepted latency, timely/late/waste/resident/outstanding outcomes and total traffic, including regressions.

Targets are not results: remove speculative demand-cache eviction, reduce repeated wasted burst traffic and preserve regular-stream benefit within a predeclared regression budget. No speedup is claimed until the upgraded RTL runs and passes all Phase 1 regressions.
