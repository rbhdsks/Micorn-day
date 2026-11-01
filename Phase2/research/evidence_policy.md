# Dataset, plotting and claims policy

This policy is a research design, not a statement that every recommended experiment has executed. The measured manifest, audit disposition and release evidence determine execution status.

## Data quality is about the access-producing process

Keep three evidence tiers separate. Directed traces isolate controller failure mechanisms. Executable numerical kernels generate documented logical operand reads, exercising real loop order and address layout. Captured application traces and full-model runs test transfer to actual software. More variants in the first two tiers do not turn them into the third tier.

Synthetic data can be useful when its properties match a stated question. MLCommons itself explains a deliberately designed synthetic recommendation workload with explicit system characteristics. The required distinction is calibration and workload validity, not a simple real/synthetic label. Our small generated kernels are useful functional and locality experiments; they have not been calibrated to a production application population. [MLCommons DLRMv3 rationale](https://mlcommons.org/2026/02/dlrmv3-inference-meta/).

For every case record algorithm, dimensions, layout, address bases/alignment, numeric type, seed meaning, operation/read count, filtered operations, line geometry, gap semantics, latency model, source hash and replay hash. A seed that varies layout is not an independent dataset. One embedding index seed is one generator realization. Do not publish a broad confidence interval by rerunning deterministic hardware input.

## Coverage to expose failure

| Axis | Positive mechanism | Required adverse case |
|---|---|---|
| Spatial locality | Contiguous word reads share lines | Sparse one-word-per-line access |
| Stream separation | Independent regular streams in different regions | Alternation inside one region; more active regions than entries |
| Region boundaries | Long in-region history | Short segments, boundary crossings and allocation changes |
| Reuse | Tiled working set and hot data | Conflicts that remain after speculative isolation |
| Predictability | Repeated positive and negative deltas | Gather, bursts and nonstationary phases |
| Timing | Compute gaps permit early arrival | Zero-gap and high-latency late-prefetch cases |
| Feedback | Waste decreases after throttling | Useful recovery and useful/waste context interference |
| Buffer pressure | One timely outstanding prediction | Capacity replacement, duplicate candidate, simultaneous consume/fill |

The largest credibility gap remains actual application integration. A next evidence tier should capture accesses from a small open-source application with a pinned license/version, real input data, numerical correctness and a documented logical-to-physical address policy. A captured operand stream still does not by itself measure full inference execution or processor IPC.

## Freeze the experiment

Declare a development subset, final held-out subset and finite parameter grid before observing final outcomes. Tune only on development data. Freeze source/thresholds before held-out runs, retain failed attempts and publish every declared case. If final results change the design, call that an exploratory iteration and create a fresh held-out set for the next confirmation. Do not relabel previously inspected traces as unseen.

Original Phase 1 patterns are regression/diagnostic cases because their results are already known. They cannot be advertised as held-out validation for the upgrade. Kernel families with a development seed and two new seeds provide a limited seed holdout within known generators, not an unseen-application test.

## MATLAB and figure audit

Each figure must read measured CSVs or clearly labelled analytical inputs. Both MATLAB and Python should implement the definitions in [mathematics.md](mathematics.md). Published images require their actual generator/runtime to be named. If MATLAB is unavailable, provide reviewed scripts and clearly identify Python-generated figures; source review or Octave compatibility is not MATLAB execution.

The most informative figure set is parallel and causal:

1. Dataset coverage: read counts, footprint and locality by family, with diagnostic/kernel labels.
2. Matched per-case completion speedup: show every policy and values below one.
3. Traffic-speedup scatter: all cases, baseline lines at one, consistent family markers.
4. Ablation deltas: isolate buffer, region and gate additions with paired comparisons.
5. Main-cache versus timely buffer hit rates: preserve definitions.
6. Prefetch fates: timely, late, waste and unresolved, with conservation checked.
7. Gap/latency sensitivity: display only sampled points; do not invent a smooth surface.
8. Slowdown distribution and worst cases: show count, threshold and sample population.
9. Per-request tail latency when logs support it; otherwise label per-case mean distributions correctly.
10. Storage/synthesis tradeoff: same tool, geometry and target assumptions.
11. A causal pollution timeline: addresses, index collision, placement and subsequent demand.
12. Feedback/recovery state timeline from actual logged events if available.

Use zero baselines for magnitude bars, meaningful log scales where needed, legible labels, consistent policy colors and absolute counts alongside small-denominator ratios. Separate analytical CDM figures from RTL performance panels. No radar chart of subjective “innovation” scores, decorative 3D bars, invented power bars or unmeasured trend surfaces.

## Double audit gates

The first pass is adversarial design/methodology review: list concrete mechanisms that can invalidate correctness, comparison or claims. The second pass is an independent inspection of implemented source, raw outputs, formulas and rendered artifacts. Closing a finding needs a linked check, not a sentence that says “resolved.”

For Level 4, inspect FSM transitions, valid/data stability, simultaneous events, late demand recheck, buffer replacement, shared reset, disable with in-flight work and mature-event attribution. Stress tests complement directed cases; neither substitutes for the other. A generic synthesis CHECK pass does not prove FPGA timing. Vivado simulation, synthesis, implementation, constraints and timing reports are separate execution gates. The exact tool, part, clock and testbench scope must be recorded; no internal company approval follows from running a vendor tool.

## Questions to prepare for judges

| Question | Evidence an answer should open |
|---|---|
| What exactly is context? | Observable input/state definition and the regional/global split |
| Why is this more than a stride counter? | Matched buffer/region/gate ablations and a case requiring each addition |
| What did the added 32 data bytes buy? | Storage table, buffer-only comparison and equal-resource control when present |
| Does it still work when addresses are laid out differently? | Address-layout variants, same-region and boundary cases |
| How do you know a prediction helped? | Timely/late first-use accounting and paired completion result |
| What happens when you predict incorrectly? | Pollution repair, nonpreemptible blocking and waste/recovery tests |
| Are these real AI workloads? | Case provenance, kernel numeric checks and explicit missing application tier |
| Why not always use next-line? | Dense stream startup benefit and irregular/stride traffic penalty |
| Does CDM run in hardware? | Explicit no; separate research and feature-extension requirements |
| What can Micron integrate today? | Standalone interface/contract and concrete remaining timing/protocol gates |
| Did Vivado prove it works on an FPGA? | Only the exact executed simulation/implementation evidence; no inferred hardware claim |
| Where does it lose? | Full regression table and weakest held-out cases |
