# Mathematical and measurement contract

This contract describes required definitions. The implemented testbench schema and measured report must state any differences explicitly. None of the analytical expressions substitutes for RTL timing.

## Demand classifications

Let N be accepted demand reads. Let Hc be demands found in the main cache at acceptance, Hb demands found only in the prefetch buffer at acceptance, and M initially unavailable demands. Classifications must be mutually exclusive:

$$N=H_c+H_b+M.$$

Publish main-cache hit rate Hc/N and timely subsystem hit rate (Hc+Hb)/N separately. Counting buffer hits as cache hits without renaming the metric makes a Phase 1/Phase 2 comparison ambiguous. A demand that waits for an in-flight speculative line is initially a miss and later a late consumption.

The Phase 2 RTL preserves the original main-cache miss counter: `hits + misses = N`, while `buffer_hits` is a subset of `misses`. Therefore Hc = `hits`, Hb = `buffer_hits`, and M = `misses - buffer_hits`. Do not add all three raw counters as if they were disjoint. The subsystem miss rate is (`misses - buffer_hits`)/N. The accepted-request scoreboards must check the preserved identity and the subset bound.

## Timing boundaries

For paired case i and policy p:

$$S_{i,p}=\frac{C_{i,\mathrm{none}}}{C_{i,p}}.$$

C ends at final demand response consumption. Report quiescent drain separately. Compute gaps, response backpressure and request offer/acceptance rules must be identical across a pair. A policy may change acceptance times, so offer-to-availability latency is essential alongside accept-to-availability latency.

For each demand j:

$$L^{offer}_j=t^{available}_j-t^{offer}_j,\qquad L^{accept}_j=t^{available}_j-t^{accept}_j.$$

Their difference is preacceptance waiting. Availability differs from response consumption when the consumer stalls. Completion includes prescribed consumption stalls; response-availability latency does not include waiting after the response is already valid.

If storing per-request latency, define percentiles with an explicit estimator. Nearest-rank p95 uses sorted latency at index ceil(0.95N), with one-based indexing. A percentile of per-run means is a different statistic and must not be labelled per-request p95.

## Timeliness and lead distance

A prediction is timely if the prefetched data are available before the first demand that needs it. The causal condition is

$$t^{demand}-t^{pf\ issue}\ge L^{pf\ service}.$$

For an approximately regular stream with d lines of lead and a roughly constant inter-line interval tau, d*tau is an approximate lead time. It is not an exact performance model: cache hits, queueing, backpressure and the serial driver's gaps make tau policy dependent. Degree one and one outstanding transfer impose structural limits. Increasing nominal distance is not guaranteed to improve coverage because it can increase wrong work and eviction.

## Prefetch fates

Let P be issued speculative line reads, T timely first consumptions, L late first consumptions, W unused replacements and R resident-unconsumed lines. At settled quiescence:

$$P=T+L+W+R.$$

If the design cancels issued work, permits outstanding work at the observation boundary or has an extra drop path, those categories must be included rather than hidden. A candidate rejected before issue is not an issued prefetch. Each issued line is charged once, at its first mature outcome or as resident unresolved state. Repeated demands must not repeatedly increment useful counts for one prefetch.

Consumed accuracy is (T+L)/P, N/A for P=0. Mature-only accuracy (T+L)/(T+L+W) excludes unresolved residents and is a different measure. Neither is an application speedup. An unused prediction is wasted traffic; proving cache pollution requires a paired demand-loss comparison or a stronger causal counterfactual.

## Traffic and useful delivery

With a 16-byte transfer and Nd demand transactions:

$$B=16(N_d+P),\qquad R_B=\frac{B_p}{B_{none}}.$$

Always publish absolute transactions with ratios: a four-transaction baseline makes a small absolute change look enormous. A repeated demand may consume several words from one fetched line, so requested bytes divided by transferred bytes can exceed one through reuse. That ratio is a service/reuse measure, not physical bus utilization. Distinct bytes actually used from each fetched line require separate byte-use instrumentation.

Do not convert B into watts or joules with an unexplained constant. A DRAM energy estimate needs device parameters, commands, activity and background time. Extra controller state and CPU runtime also affect system energy. [Micron power calculator](https://www.micron.com/sales-support/design-tools/dram-power-calculator), [DRAMPower inputs](https://github.com/tukl-msd/DRAMPower).

## Aggregate results

For K declared matched cases, geometric mean speedup is

$$G_p=\exp\left(\frac{1}{K}\sum_{i=1}^{K}\log S_{i,p}\right).$$

Do not average percentages or divide unrelated mean times. Report aggregation groups and weights: 20 variants of one family should not silently outweigh one case of another. Show per-family summaries and the full case distribution. A ratio of summed cycles is a valid total-work metric only when the chosen mix and its weights are explicit; it answers a different question.

Report median, worst speedup, count below one, and a declared substantial-regression threshold, for example below 0.95. A tolerance of 5% is a design choice, not a standard or proof of acceptability. Keep a traffic-speedup Pareto view instead of hiding tradeoffs in an arbitrary weighted score.

## What the quality gate can infer

For a proposed prefetch, an ideal expected utility would involve useful probability p, latency benefit b, harm cost h and resource cost r:

$$E[U]=p b-(1-p)h-r.$$

The small counter observes only coarse useful/waste outcomes. It does not estimate all those quantities; even p is delayed, censored by residents and affected by eviction. Therefore its threshold is a bounded heuristic, not an optimal controller. Keep training and recovery behavior explicit, and evaluate interference between useful and wasteful contexts under a global gate.

## Hardware cost

Two buffers holding 128 data bits, 28 identity bits and one valid bit require at least 314 logical bits, before replacement/control or attribution metadata. Region state must be counted from actual RTL widths. Compare same-tool generic cell totals and logical storage, not generic cells versus vendor LUT counts or another paper's area.

The extra 32 data bytes increase capacity beyond the baseline's 1 KiB. Buffer-only ablation measures added context/feedback value but does not prove that the buffer is the best use of those resources. A strict fixed-budget claim also needs an equal-resource demand victim-buffer or cache-capacity control. Synthesis CHECK success is structural evidence, not timing closure or energy characterization.
