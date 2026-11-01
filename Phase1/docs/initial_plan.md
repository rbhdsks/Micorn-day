# AI-Aware Cache & Prefetch Engine RTL Challenge — project plan

## Objective and source of requirements

Design a cache and a prefetch engine that reduce the time an AI workload spends waiting for memory, then demonstrate correctness and performance against a baseline.

This plan is based on the two challenge slides supplied on 1 November 2026. The slides describe five progressive levels and say to start at Level 1 and go as far as possible. They do not specify a submission portal, deadline, trace format, fixed architecture, grading rubric, or whether every level is mandatory. Recommendations below are our proposed workflow, not additional official requirements. The project folder initially contained no files or traces.

The task is memory-system hardware, not training an AI model. “AI-aware” does not establish a requirement to implement a neural predictor: the slides explicitly allow sequential and stride strategies.

## Memory-system idea

- A cache is small, fast storage near compute; DRAM is larger and slower.
- A demand request hits if its data is in the cache; otherwise a miss requires a fetch.
- A prefetch engine observes demand accesses, predicts future cache lines, and fetches them early.
- Useful prefetches must be correct and timely. Incorrect or excessively early prefetches can waste bandwidth and evict useful data.
- Prefetching can reduce demand stalls while increasing total DRAM traffic. Measure both.

## Level 1 — memory trace analysis

Goal: establish which access patterns actually exist before choosing hardware.

1. Obtain the official trace and specification, or clarify how traces should be generated.
2. Record provenance: workload, input, generation method, access types, address units, ordering, timestamps, request sizes, and available instruction/stream identifiers.
3. Validate parsing and preserve the original trace. Do not assume hexadecimal for unprefixed numbers.
4. Analyse both byte addresses and cache-line addresses. For a 64-byte line, 0x1000, 0x1004, and 0x1008 belong to the same line.
5. Measure access count, unique lines, working-set size, frequent lines, line-address deltas, adjacent same-line accesses, reuse gaps, and coarse memory regions.
6. Look for sequential streams, fixed strides, repeated lines/regions, phase changes, and irregular behaviour. Interleaved streams may obscure a pattern in the combined trace.
7. Inspect whether the trace is representative and whether its access order and timing support the conclusions being drawn.
8. Produce an analysis report with evidence, limitations, and candidate prefetch strategies. Synthetic examples validate the tooling; they are not AI-workload evidence.

Deliverables: reproducible analyser, input-format documentation, summary tables/plots as appropriate, and a report on the actual workload once supplied.

Completion gate: the real trace is understood and initial design choices can be justified from its measurements. Tooling alone does not complete Level 1.

## Level 2 — cache architecture design

Specify capacity, line size, associativity, replacement, writes if applicable, interfaces, outstanding transactions, refill handling, and prefetch insertion.

Illustrative configuration only: 4 KiB of data, 64-byte lines, two ways, 64 total lines, 32 sets. A byte address then has six offset bits, five index bits, and remaining tag bits. Metadata adds storage beyond data capacity.

Understand direct mapping versus set associativity; justify LRU, pseudo-LRU, FIFO, or another replacement choice. Establish whether actual data storage/return checking is required or an address/tag model is sufficient. Plan for data correctness unless the official scope says otherwise.

Recommended workflow: build a small software cache model before RTL. Use it to establish a no-prefetch baseline and explore configurations cheaply.

Deliverables: cache specification, address mapping, block diagram, interface/timing rules, and rationale.

## Level 3 — prefetch strategy design

Start with next-line prefetching as a reference. Compare a stride predictor if the trace supports it. Example: line addresses 100, 104, 108, 112 suggest stride +4 and candidate 116.

Define:

- Trigger: each demand, a miss, or another event.
- Distance: how far ahead to fetch.
- Degree: number of candidates per trigger.
- Confidence: evidence needed before predicting.
- Filtering: suppress cached and already-outstanding lines.
- Arbitration: prioritise and coordinate demand and speculative traffic.
- Insertion/replacement: control cache pollution.
- Predictor indexing: global, per instruction, per region, or another justified choice.
- Resource bounds, reset behaviour, and address boundary/overflow behaviour.

A correct next-line prediction may still arrive too late if memory latency exceeds the available lead time. More lookahead costs bandwidth and capacity. Choose from evidence rather than complexity.

Deliverables: algorithm, pseudocode, predictor state/storage, expected strengths and failure modes, and software-model comparisons.

## Level 4 — RTL implementation

The slides explicitly name Verilog/SystemVerilog, a cache controller, prefetch engine, and testbench.

Proposed components:

- Trace/workload driver.
- Cache data, tags, valid bits, and replacement metadata.
- Cache controller for lookup, miss, refill, and response.
- Prefetch predictor observing demand accesses.
- Request arbitration and outstanding-request tracking.
- DRAM contents/timing model.
- Self-checking testbench and statistics.

The slide's vertical diagram is conceptual; the predictor need not sit serially on every data response path.

Define when requests are accepted, backpressure, response validity, response matching, and the number of in-flight requests. One outstanding transaction simplifies verification but can limit overlap and prefetch benefits.

Verify the cache first, then add prefetching. Check returned data, conflicts/eviction, repeated accesses, refill, reset, duplicate prefetch suppression, demand/prefetch contention, and applicable writes. Incorrect returned data invalidates a performance result.

Deliverables: RTL, memory model, testbench, tests, simulation commands, and representative evidence. Synthesis/FPGA work is conditional on official requirements.

## Level 5 — performance validation

Compare the same cache with prefetch disabled, next-line prefetch enabled, and the proposed predictor. Keep workload, cache capacity, memory timing, and request-driver assumptions fixed. Report predictor resource overhead separately.

Metrics:

- Demand hit rate = demand hits / demand accesses.
- Total completion cycles and average demand latency.
- Speedup = baseline completion cycles / proposed completion cycles.
- Prefetch accuracy: define the denominator and when a fetched prefetch is considered useful.
- Total memory traffic and unused prefetched lines.
- Where feasible: timeliness, miss coverage, and harmful evictions.

Do not count prefetch accesses as demand hits. State warm-up, measurement interval, draining/end-of-trace rules, and treatment of unused lines. Address-only traces require an explicit execution/timing model; hit rate alone does not prove application speedup. If coverage is estimated by miss reduction, distinguish that from exact per-access baseline-miss coverage.

Deliverables: reproducible results, comparison tables/plots, correctness evidence, and honest tradeoffs/limitations, including workloads where prefetching hurts.

## Proposed submission package — not an official checklist

1. README: scope, completed levels, prerequisites, exact run commands.
2. Trace analysis: provenance, statistics, patterns, plots/tables, conclusions.
3. Design report: cache architecture, predictor, interfaces, assumptions, alternatives, overhead.
4. RTL and supporting logic.
5. Verification: testbench, memory model, meaningful correctness tests.
6. Results: fair baseline comparison, metrics, limitations.
7. Reproduction scripts; respect trace redistribution restrictions.
8. Presentation/demo if requested by organisers.

Submission location, exact file types, naming, and deadline remain unknown.

## Questions for the organisers

- Are traces supplied or generated by participants? What format and workloads?
- Are addresses byte-addressed? Are reads, writes, timestamps, sizes, and PCs provided?
- Are cache capacity, line size, interface, memory latency, and outstanding-request limits fixed?
- Is a functional data cache required? What memory/coherence scope applies?
- Which simulator/toolchain is expected? Is synthesis or FPGA validation required?
- Are all levels required, and how are partial solutions evaluated?
- What must be submitted, where, and by when? Are external code/tools and trace redistribution permitted?

## Execution order and current status

- [x] Save the explanation and working plan.
- [x] Inspect initial folder: no trace or official brief present.
- [x] Level 1: implement and verify initial trace-analysis tooling (five tests passed; synthetic example analysed).
- [ ] Level 1: obtain and validate actual workload trace and format.
- [ ] Level 1: analyse actual workload and write evidence-based conclusions.
- [ ] Level 2: implement baseline cache software model; specify architecture.
- [ ] Level 3: compare next-line and candidate predictors; choose design.
- [ ] Level 4: implement and verify RTL cache, then prefetching.
- [ ] Level 5: evaluate and prepare submission package.

Git initialisation and branches are being handled by the user. Do not initialise Git or change branches as part of this setup.

## Modelled matrix-multiplication starting experiment

User authorised a locally generated matrix-multiplication example and an analysis notebook. `level1/generate_matmul_trace.py` generates explicit algorithm-level A/B/C accesses for `ijk` and `ikj`, and checks numeric outputs. `level1/matmul_analysis.ipynb` generates traces, plots access patterns and reuse, and writes evidence and limitations under `level1/results/modelled_matmul/`. These are modelled accesses, not captured CPU/GPU accesses. This starts Level 1 exploration; actual workload validation and official trace acceptance remain open.
