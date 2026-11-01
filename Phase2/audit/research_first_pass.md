# First audit: design, research and evidence

Audited baseline: Phase 1 commit `7851de10f6311847ded4ff04640c678ba3999437`. Review date: 1 November 2026. This is the first, adversarial pass. “Gate” states the evidence needed for closure; it does not imply the Phase 2 implementation already passes. The second audit must inspect actual source and retained results independently.

| ID | Severity | Finding and baseline evidence | Required gate |
|---|---|---|---|
| R01 | High | “Context aware” can overstate a single global address-history register (`Phase1/level4/rtl/stride_prefetcher.sv`) | Name observable context; show regional history and global outcome-control ablations; retain same-region and boundary failures |
| R02 | High | Speculative fills replace demand data. `pollution_return` grows from 4 to 132 transactions under stride and slows down | Isolate speculative placement; assert fill destinations; reproduce original address collision without extra pollution misses |
| R03 | High | Global deltas mix independent operand streams. Both imported A/B subsets show no stride gain | Region-separated history comparison; distinguish stream interference from remaining cache conflicts |
| R04 | High | Feedback can be oversold as utility learning. Frequency of consumption omits benefit magnitude, queue harm and unresolved residents | Document mature events and counter policy, recovery bounds and global interference; do not claim optimal control |
| R05 | High | Baseline traces are directed/modelled, one irregular seed, artificial gaps and immutable A/B filtering | Expand documented numerical kernels, seeds/layouts and timing cases; keep synthetic/operand/application tiers distinct |
| R06 | High | Serial one-outstanding replay cannot establish memory bandwidth saturation, MLP, IPC, CXL/HBM throughput or inference speedup | Restrict current claims; require a processor and command/timing-aware memory integration for those stronger results |
| R07 | High | One positive plot can hide workload regressions or tiny denominators | Publish complete matched results, absolute traffic, slowdown distribution and a Pareto view; use correct aggregation |
| R08 | High | Main-cache misses include timely buffer hits in the retained counter convention | State `unavailable_misses = misses - buffer_hits`; check `hits + misses = accesses` and subset bound; publish separate hit definitions |
| R09 | High | Additional buffer data and region metadata are extra resources | Count actual widths and synthesis deltas; add equal-resource demand storage control for strict budget comparisons |
| R10 | High | Simultaneous consume/refill/replacement/reset paths can miscount useful work or return stale data | Independent data scoreboards and directed event-order tests; check prefetch fate conservation after natural drain |
| R11 | Medium | Original diagnostics are already known, so cannot be relabelled unseen validation | Declare development and limited seed holdout before evaluating; freeze thresholds; record tuning history |
| R12 | High | CDM choice-set context is different from telemetry; six supplied initial-factor observations are not trained policy evidence | Keep CDM separate; explicitly define any proposed feature extension and held-out learning experiment |
| R13 | High | Generic synthesis is not FPGA timing validation; no target part, constraints, implementation or board run were established by Phase 1 | Record exact tool/part/clock; separately execute vendor simulation, synthesis and timing gates when available; report unavailable steps |
| R14 | Medium | MATLAB source existed without MATLAB runtime execution | Expand matching source and arithmetic checks; identify actual plot runtime; execute MATLAB only if present and keep its logs |
| R15 | High | No source establishes novelty or superiority over advanced prefetch research | Cite stream-buffer, table, local-delta and feedback prior art; claim compact verified integration rather than invention |
| R16 | Medium | Traffic reductions do not imply proportional energy savings | Use command/activity/device-aware modelling or remove power numbers; distinguish logical storage and process memory |
| R17 | Medium | Company relevance can slide into unsupported company approval | Ground motivation in official Micron tradeoffs; no certification, endorsement or unpublished scoring claim |
| R18 | Medium | A polished deck can obscure a non-runnable result | Make every chart traceable to raw evidence; provide source, commands, complete tables and a short reproducible demonstration |

## Level assessment before the upgrade

| Level | Existing strength | Deep-work gap |
|---|---|---|
| 1 Trace analysis | Explicit parser/geometry/provenance and numerical matrix generator | Broader kernels, layouts, phases and eventually captured application access streams |
| 2 Architecture | Inspectable direct mapping and full read-only contract | Resource-equivalent comparison, bounded regional/buffer organization and FPGA implementation assumptions |
| 3 Strategy | Repeated-delta state and negative examples | Measurable contextual conditioning, mature feedback, recovery and interference analysis |
| 4 RTL | Ordered data checking, stress, stalls and structural synthesis | New event-order paths, independent new tests, target-specific FSM/synthesis/timing methodology |
| 5 Validation | 39 paired RTL runs with fair timing endpoints | Broader declared experiment, ablations, tail/distribution analysis and strict claim audit |

## Relevance and competitive interpretation

The best improvement is stronger engineering evidence, not extra adjectives or a larger number of charts. A credible differentiator is the causal chain: observe an actual failure, repair one mechanism, isolate its value, account for the resources, and show where the repair does not transfer. No comparison data about other participants or published internal Micron certification criteria was supplied. This audit cannot establish a winning probability, product readiness or company approval.

Sources and mathematical gates are in [the research directory](../research/README.md). Later audit dispositions must identify which gates executed, which failed and which remain open.
