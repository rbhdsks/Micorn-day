# Predeclared evaluation plan

Frozen design defaults: 64 direct-mapped 16-byte cache lines, two 16-byte buffer entries, four region histories, 4 KiB regions, two-bit global quality initialized to two and a 16-accepted-demand recovery probe interval. These are inspectable design choices, not thresholds fitted to held-out results. Intervals eight and 32 are explored only on validation cases and do not change the final default.

## Cases and comparison protocol

The primary experiment replays 55 declared cases through all seven variants, for 385 runs. The 10 validation cases are four numeric families at seed11 and two gap settings plus WikiText train input at two gaps. Twenty held-out cases comprise two held-out shape/layout seeds and WikiText published validation/test input. Thirteen original regressions and 12 boundary/interference timing stresses are reported separately. Probe sensitivity adds 20 validation-only runs; total405. Cases are never dropped after observing results.

Every matched case uses the same addresses, post-response gaps, 1 KiB main-cache geometry, deterministic memory model and request-index modulo4 consumer-stall schedule. The driver serializes demands, so gap zero is not a pipelined full-rate CPU. Memory countdown values0/12/48 expose sensitivity; they are not nanoseconds or physical DDR timings. Completion ends at consumption of the last demand response and excludes the unused final gap. Natural speculative drain is separate.

The runner compiles the original Phase 1 RTL for none/next-line/stride and the upgraded RTL for buffer variants. The adapted baseline bench only adds zero-cycle file output. All original13×three reference completion, hit/miss, traffic and fate values must match exactly. Per-request output samples must reconcile with measured latency sums/maxima. Every returned word is checked against the address-derived backing-memory reference.

## Selection rule fixed before held-out execution

Eligible proposed upgrades are victim_buffer, global_buffer, region_buffer and context_feedback. Select the highest **family-balanced geometric mean completion speedup** on validation, subject to a family-balanced geometric mean DRAM-transaction ratio at most1.25 relative to none. This25% traffic allowance is an explicit experimental design budget, not an official judging rule or Micron product requirement. If no upgrade qualifies, publish no selected upgrade. Ties rounded to12decimals choose the stated simpler-order list above. The runner writes and hashes `selection.json` before any held-out commands. No held-out result changes thresholds, dataset membership or selected variant.

The next-line and stride references remain visible even though the selection rule chooses among the proposed upgrades. Publish Pareto frontiers for speedup versus traffic for all seven variants, plus worst-case and p95-case completion ratios. A selected policy can lose on individual workloads. If a simpler victim buffer dominates the context design, that is evidence against the context claim and must remain visible.

## Formulas and aggregation

For case i and variant v, demand hit rate is `H_iv/N_i`, service hit rate is `(H_iv+B_iv)/N_i`, completion speedup is `C_i,none/C_iv`, traffic ratio is `D_iv/D_i,none`, bytes are `16D_iv`, and consumed prefetch accuracy is `(T_iv+L_iv)/P_iv` when `P_iv>0`, otherwise N/A. Buffer and late hits never silently change main-cache hit classification. Victim-buffer hits are excluded from prefetch accuracy.

For positive paired ratios r_i in family f, `G_f=exp(mean_i(log(r_i)))`. The family-balanced summary is `G=exp(mean_f(log(G_f)))`; each of the five input families receives equal weight despite differing read counts. The case-weighted geometric mean is additionally published. Neither is an arithmetic average of speedups or a ratio of total runtimes. Absolute accesses and total transactions accompany normalized ratios.

Nearest-rank empirical quantile q is sorted sample index `ceil(q*n)-1` (zero based). Per-request p50/p95 offered latency uses that run's request samples. Across-case p95 completion ratio describes finite suite outcomes, not a statistical confidence interval. Worst completion ratio is `max_i(C_iv/C_i,none)`; a ratio above1 is a slowdown. Also report the count of cases with speedup below1.

After quiescence, `P=T+L+U+R`: issued speculative reads partition into first timely consumption, first late consumption, unused replacement and still-resident unconsumed lines. Still-resident outcomes are unresolved and remain in the accuracy denominator. Unused replacement alone does not prove harm to demand reuse. The separate buffer structurally avoids speculative demand-cache replacement, but can still waste memory transactions or block demand behind a selected nonpreemptible fetch.

## Limits and anti-cherry-picking controls

The two gaps of one sequence are correlated conditions. Two held-out kernel seeds are a small shape/layout exploration, not a random sample of real applications. Repeating deterministic traces adds reproducibility, not confidence. No bootstrap over individual memory accesses is presented as application uncertainty. Report all families and negative cases, source/input hashes, selected configuration, exact commands and execution status. Authentic WikiText input order, numeric kernel correctness and actual instruction traces are distinct evidence levels. No real model inference timing, bandwidth-saturation, MLP, power or target timing claim follows from this driver.
