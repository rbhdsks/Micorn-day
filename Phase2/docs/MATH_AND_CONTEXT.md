# Mathematical basis and the meaning of context

## Observable context

Let the accepted byte address be a and the fixed line size be 16 bytes. The line number is floor(a/16), the direct mapped index is line mod64 and the address region is floor(a/4096). Region history lets distinct address regions retain distinct recent deltas. It cannot distinguish independent objects that share a region, or infer a program counter that is absent from the interface.

The proposed controller combines a region predictor with a separate two entry speculative buffer. A global mature outcome counter can suppress new predictions after repeated unused replacements and permits periodic recovery probes. Prediction confidence counts repeated deltas. Outcome quality counts consumption or unused replacement. They measure different events and must not be called the same probability.

This is context awareness through bounded observable state. It does not establish tensor semantics, application intent or a trained AI model. CDM in the supplied notes models the effects of available alternatives on a choice. Conditioning a selector on cache telemetry requires a new explicit feature model and its own held out evaluation. Phase 1 CDM research remains separate.

## Performance definitions

For N accepted demand accesses, H main cache hits and B timely speculative buffer hits,

$$h_{cache}=H/N,\qquad h_{service}=(H+B)/N.$$

Completion C ends at the final consumed demand response. Quiescence additionally drains outstanding speculative work. For the same replay case i and variant v,

$$s_{i,v}=C_{i,none}/C_{i,v},\qquad r_{i,v}=D_{i,v}/D_{i,none}.$$

D counts all memory line transactions. Bytes transferred are16D. Offered latency includes time waiting for acceptance; accepted latency starts at the request handshake. Percentiles describe the per request samples in that replay, not a population of real applications.

## Aggregation and selection

The geometric mean speedup is

$$G_v=\exp\left(\frac1n\sum_i\log(s_{i,v})\right).$$

For family balanced aggregation, average log ratios within each family first, then average those family means. This gives every declared family equal weight regardless of how many timing cases it contains. A ratio of total or average cycles answers a different question and must not be labelled the geometric mean.

Select a variant using validation cases only under the declared traffic budget. Freeze that choice before evaluating held out cases. The budget, eligibility set and tie rule belong in the selection record. If no variant qualifies, the result is a failed gate. A per case oracle uses future outcome information and serves only as an offline upper envelope over the tested candidates.

The finite experiment can identify the best eligible tested variant for a stated objective. It cannot prove optimality over all cache architectures, data sets, process technologies or application schedules.

## Conservation and mature evidence

After quiescence, each issued prefetch must have exactly one fate:

$$P=U_{timely}+U_{late}+W_{unused}+R_{resident}.$$

Resident data has not reached an outcome. It must not be scored as waste or success by feedback. A buffer replacement is waste only if that particular prefetched line has never been consumed. The consumption accuracy is (Utimely+Ulate)/P when P is nonzero. Immediate local service and a late merged demand are reported separately.

## Time and traffic tradeoffs

Represent a declared transaction penalty by lambda cycles per line transaction:

$$J_v(\lambda)=C_v+\lambda D_v.$$

If a faster variant issues more transactions, its break even penalty is

$$\lambda^*=\frac{C_{base}-C_v}{D_v-D_{base}}.$$

This sensitivity analysis expresses a preference over two measured quantities. It is not an energy estimate or physical memory simulator. A variant that lowers both C and D dominates that reference in those two quantities, while hardware cost can still favor the simpler design.

## Storage and relevance to memory systems

Two extra lines hold32 data bytes. Their full identities, valid bits, replacement state and all predictor metadata add more bits. Equal extra data bytes do not imply equal area, power or timing. Generic synthesis cell counts are tool dependent and require common tool/constraints for relative comparison.

A single outstanding full line interface cannot measure many channel memory bandwidth or bank contention. More detailed conclusions require a validated memory timing model, realistic concurrency and captured application traces. The applicable engineering question here is how many useful demands the cache serves per simulated transaction under the declared latency and gap assumptions.
