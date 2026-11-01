# Primary-source research and claim map

Checked 1 November 2026. Dates below are the source's publication/version dates when stated; undated living pages are marked as such. This review establishes relevance and prior art. It does not borrow external performance numbers as results for this RTL.

## Why the problem matters to a memory company

Micron's official AI material treats bandwidth, capacity, latency and power as workload-dependent constraints across a memory/storage hierarchy. That supports a motivation around useful data movement. It does not validate this project's architecture or make its simple memory model equivalent to a Micron device. [Micron AI data center, living page](https://www.micron.com/markets-industries/ai/ai-data-center).

Micron's edge-AI material also emphasizes responsive access and power-efficient memory. A small bounded controller is consequently a more credible integration discussion for a constrained compute subsystem than a claim to solve data-center HBM performance. The prototype still lacks target timing, a power model and an actual application integration. [Micron Edge AI, living page](https://www.micron.com/markets-industries/ai/edge-ai).

A Micron CXL experimental paper uses real modules, a specified processor, memory channels and page interleaving. It illustrates the evidence needed for system-level bandwidth claims. Our serial one-outstanding model supplies none of those CXL protocol or channel effects. [Sehgal et al., submitted 17 December 2024](https://arxiv.org/abs/2412.12491).

## Prior art and what it prevents us claiming

| Source and date | Relevant established idea | Consequence for this project |
|---|---|---|
| [Jouppi, ISCA, May 1990](https://doi.org/10.1145/325164.325162) | Small associative structures and prefetch buffers improve direct-mapped cache behavior; speculative data can be kept outside the demand cache | Buffer isolation is an engineering implementation, not a new invention |
| [Chen and Baer, IEEE TC, May 1995](https://homes.cs.washington.edu/~baer/chenieee.pdf) | Past access patterns in a reference prediction table; timing/lookahead and memory restrictions affect usefulness | A repeated-delta table is a basic baseline; timeliness and interference need experiments |
| [Srinath, Mutlu, Kim and Patt, HPCA 2007](https://hps.ece.utexas.edu/pub/srinath_hpca07.pdf) | Feedback combining accuracy, lateness and cache pollution adjusts speculation and placement | A useful/waste counter is narrower than comprehensive feedback; it cannot be advertised as its invention or equivalent implementation |
| [Navarro-Torres et al., Berti, MICRO, October 2022](https://webdiis.unizar.es/~chus/pubs/berti/berti.html) | Local per-instruction deltas and timely prediction address information lost by global deltas | Our region proxy has no authentic instruction identity and is not Berti or a demonstrated improvement over it |
| [Wong et al., Caerus, arXiv v1, 29 October 2026](https://arxiv.org/abs/2610.39797v1) | Multiple global offsets combined with local per-PC accuracy filtering; source reports acceptance to MICRO 2026 | “Thinking locally” and context-sensitive filtering already have advanced prior art; cross-paper speedup comparisons would be invalid |
| [Huang, Wong and Ainsworth, Proba, arXiv v3, 28 October 2026](https://arxiv.org/abs/2610.30448v3) | Spatial patterns with probabilistic updates and feedback control of accuracy/coverage; source reports acceptance to PACT 2026 | Adaptive low-traffic prefetching remains an established research area; our small gate is a bounded simplification |
| [Seshadri, Peysakhovich and Ugander, ICML, 2019](https://proceedings.mlr.press/v97/seshadri19a.html) | Context effects arise from the alternatives in the available choice set; low-rank interactions model these effects | CDM “context” must not be silently redefined as cache pressure, application semantics or address history |

The 2026 preprints are author primary sources with the acceptance statements noted above. They have not been independently reproduced here. Their results, storage budgets, workloads and architectural assumptions differ from this project; no numerical superiority claim is made.

## Evaluation and model sources

| Primary source | What it supports | Application and boundary |
|---|---|---|
| [ChampSim official documentation, living](https://champsim.github.io/ChampSim/develop/) and [repository](https://github.com/ChampSim/ChampSim) | Trace-based processor/cache evaluation, authentic trace generation and explicit warmup/simulation boundaries | An established future generalization path; current RTL replay is not a ChampSim IPC experiment |
| [MLCommons inference benchmark page, living](https://mlcommons.org/benchmarks/inference-datacenter/) and [rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc) | Inference evaluation requires defined model, dataset, quality and scenario performance requirements | The project is not an MLPerf run; address replay cannot establish model-quality-preserving inference speedup |
| [MLCommons DLRMv3 rationale, February 2026](https://mlcommons.org/2026/02/dlrmv3-inference-meta/) | Synthetic data can be representative when designed for explicit model/system characteristics, including evolving histories and large embedding spaces | Synthetic is not automatically invalid. Our small skewed-gather generator remains a diagnostic, without production calibration |
| [MLCommons DLRMv2 reference README, living](https://github.com/mlcommons/inference/blob/master/recommendation/dlrm_v2/pytorch/README.md) | A real recommendation benchmark includes model, preprocessing and declared validation/calibration data | A “gather” trace is not DLRM. Importing a dataset name without its access-producing model is insufficient |
| [Ramulator official repository, living](https://github.com/CMU-SAFARI/ramulator2) | Command/timing-aware DRAM and controller simulation with explicit configurations | A future latency/bandwidth integration should pin a version and configuration; no Ramulator run is implied here |
| [DRAMPower official repository, living](https://github.com/tukl-msd/DRAMPower) | Energy estimation consumes a memory specification, command trace and activity configuration | Transactions alone cannot establish DRAM joules or system power savings |
| [Micron DRAM power calculators, living](https://www.micron.com/sales-support/design-tools/dram-power-calculator) | Device/system assumptions and access schemes determine estimated memory power | Use a disclosed device-specific estimate before claiming power; no calculator result is claimed here |
| [SPEC CPU2017 license documentation](https://www.spec.org/cpu2017/Docs/licenses.html) | Source, inputs and reporting tools have distinct redistribution restrictions | Public availability of a trace link does not establish a blanket right to redistribute every underlying benchmark artifact |

## Claim-to-evidence matrix

| Proposed statement | Evidence that may support it | Evidence that does not support it |
|---|---|---|
| “Earlier demand delivery in our subsystem” | Matched RTL completion/offer-latency results and data correctness | A predictor-only Python model or hit rate alone |
| “Less speculative waste” | Issued transaction fates after settled quiescence | Fewer resident unresolved predictions at an arbitrary stop time |
| “No speculative replacement of demand lines” | RTL placement path plus directed pollution test | A single average hit-rate improvement |
| “Lower memory traffic” | Demand plus speculative read transactions at the same line size | Prefetch count alone or an undocumented traffic denominator |
| “Context improves this design” | Region and gate ablations with matched resource accounting | Comparing the full upgrade only with no-prefetch |
| “Small bounded implementation” | Actual register widths and same-tool synthesis deltas | Source-line count, generic-cell/LUT substitution or another paper's area |
| “Micron-relevant concern” | Official memory tradeoffs plus our bounded measurement question | An implication of Micron endorsement, integration or certification |
| “Energy efficient” | Validated command/activity/device model or physical measurements | Traffic percentage multiplied by a guessed constant |
| “Faster real AI inference” | Correct full model, representative data and end-to-end timing | Immutable operand-address replay with artificial compute gaps |

## Limits of competitive claims

No dataset of competing submissions or published judging rubric was supplied. We cannot substantiate “unlike all other participants,” “best architecture,” or a winning probability. We can make the work more reviewable and persuasive by showing causal evidence, real limitations, resource costs and a live reproducible result. There is no basis to claim internal Micron design certification or approval: published product pages establish context, not unpublished evaluation criteria or an endorsement.
