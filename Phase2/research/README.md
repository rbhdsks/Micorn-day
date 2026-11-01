# Research decision: useful context under a bounded hardware budget

Research checked on 1 November 2026. This directory records the reasoning and claim boundaries for the Phase 2 upgrade. The frozen Phase 1 evidence remains the comparison baseline. Design intentions below become results only after the corresponding RTL experiment passes.

The strongest defensible project is a **small, inspectable memory-side speculation controller that separates address contexts, protects demand data and reacts to observed prefetch outcomes**. Its contribution is the implementation and evidence: ordered data-correct RTL, bounded state, stage-by-stage ablations, source-linked measurements, visible failure cases and a reproducible presentation. Region tracking, stream buffers and feedback are established ideas. Calling the combination a new AI algorithm would weaken the case.

Read [the context debate](context_debate.md), [the mathematical contract](mathematics.md), [the primary-source review](literature_review.md), [the dataset and claims policy](evidence_policy.md), and [the first audit](../audit/research_first_pass.md).

## The practical question

Can a very small cache subsystem deliver demanded data earlier while avoiding excessive speculative transactions and demand-cache eviction, when access streams alternate or change phase?

That question is specific enough to test. It also matches a memory-system design concern: latency, traffic, capacity and implementation cost interact. It does not require pretending that this 1 KiB prototype is an HBM controller, a coherent CXL device or a complete inference accelerator.

## Design interpretation agreed with the RTL implementation

- Four bounded history entries separate demand observations by 4 KiB address region. This is a proxy for stream context; it is not a program counter, tensor identity or learned semantic label.
- A two-entry fully associative prefetch buffer holds speculative data separately from demand-cache lines. Demand consumption promotes data into the demand cache.
- A **global**, two-bit outcome-quality gate uses mature useful/wasted events and bounded recovery probes. Outcome quality is not per-region learning, and the gate is not a mathematically optimal utility estimator.
- Fixed global-stride, buffer-only, region-plus-buffer and feedback ablations separate causes. No-prefetch and next-line remain simple references.

## What would make the project convincing

Show the original pollution failure and its causal repair. Then show a distinct-region interleaving case that needs separate history, a waste/recovery case that tests the gate, and the cases where the upgrade loses. Publish the same complete table behind every chart. Pair speedup with traffic and hardware cost. A live demonstration should let a reviewer change a latency or workload and rerun the experiment.

The evidence must decide the headline. If feedback adds little after buffering, describe buffering as the effective repair and feedback as inconclusive. If region tracking hurts boundary-heavy accesses, show that tradeoff. Claims about all participants, company adoption or winning likelihood cannot be established from these experiments.
