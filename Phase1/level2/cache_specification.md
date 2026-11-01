# Level 2: Phase 1 cache specification

Phase 1 is a small, functional read-only cache with selectable next-line and
stride prefetch policies. The same cache and memory controller are used for all
Level 5 policy comparisons. The geometry is a **project baseline choice**, not a
fixed organizer specification or a claim of optimal AI hardware.

[Architecture diagram (SVG)](cache_architecture.svg) ·
[Editable diagram (Mermaid)](cache_architecture.mmd) ·
[RTL](../level4/rtl/ai_cache.sv) ·
[Prefetch strategy](../level3/prefetch_strategy.md)

## Decisions and reasons

| Decision | Phase 1 specification | Reason and tradeoff |
|---|---|---|
| Data capacity | 1 KiB; 64 resident lines by default | Keeps the implementation inspectable and makes locality/conflict effects measurable. It is deliberately small, not a model-weight capacity recommendation. |
| Cache-line size | 16 bytes; four 32-bit words | Retains the verified core's fixed 128-bit refill interface. It captures spatial locality without changing the datapath. Other line sizes require RTL changes, not merely a trace-analysis option. |
| Associativity | Direct mapped: one slot per index | One indexed comparison and deterministic replacement simplify validation. Useful lines that map to one slot can evict each other. |
| Replacement policy | Incoming line replaces its indexed slot | No LRU/FIFO policy is needed when there is only one way. Speculative fills compete with demand lines in Phase 1. |
| Write policy | Writes are unsupported; no dirty bits | The data contract is aligned reads from immutable backing memory. Modelled mutable C reads/writes are excluded from the Level 5 A/B-input subset. |
| Request handling | One queued demand miss; one memory transaction outstanding | Simple response ordering and duplicate-read prevention. A queued miss blocks further CPU acceptance; no MSHRs or demand hit-under-miss are implemented. |
| Prefetch placement | Ordinary cache fill with a prefetched marker | Preserves the audited baseline and permits a small hardware implementation. Wrong prefetches can pollute the demand cache; a separate buffer belongs to Phase 2. |
| Interfaces | Single clock, ready/valid request/response channels | Producers retain payload under backpressure; consumers accept only on a rising-edge handshake. |
| Addressing | 32-bit byte address; naturally aligned 32-bit reads | Four-byte words, little-endian word placement within a 16-byte line. No unaligned/cross-line request machinery. |
| Memory errors/coherence | Not supported | This is a trace-driven read subsystem, not a coherent CPU cache or DDR/AXI controller. |

## Evidence behind the starting choices

Nitesh's [modelled matrix analysis](../level1/results/modelled_matmul/analysis.md)
records row-major four-byte elements. Its `ijk` inner B stream advances by
`N*4 = 128` bytes for N=32; `ikj` advances by four bytes within each row. These
observations justify **testing** both a signed-stride policy and a next-line
reference. They do not establish that a 1 KiB direct-mapped cache is optimal.
Interleaved A/B/C addresses can hide the individual operands' regularity.

The archived notebook counts 64-byte lines. Phase 1 RTL has 16-byte lines: the
same 128-byte B step becomes **eight RTL lines**, while four consecutive words
fit in one RTL line. Level 5 re-analyses its replay inputs at 16 bytes. A line
count, reuse gap or footprint from Level 1 is not a measured hit rate.

The assigned A/B/C bases are page aligned. Their first lines map to the same
cache index in this direct-mapped design, so placement can create conflicts.
Consequently, Level 5 includes both disjoint-set and conflicting-stream cases.
No cache-capacity or associativity superiority is claimed without a sweep.

## Address decomposition

For the default `INDEX_BITS=6`:

```text
32-bit byte address
31                  10 9           4 3       2 1       0
+---------------------+-------------+---------+---------+
| conventional tag    | index (6)   | word(2) | byte(2) |
+---------------------+-------------+---------+---------+

line identity = address[31:4]       (28 bits stored in the RTL)
index         = line_identity[5:0]
word          = address[3:2]
line request  = {line_identity, 4'b0000}
```

A hit requires `valid[index] && tags[index] == line_identity`. The stored
identity includes the index, simplifying inspection at a small metadata cost.
Address `0x1234` selects line `0x123`, index 35, word 1, with refill address
`0x1230`. Addresses `0x1000` and `0x1400` both map to index zero and have different
identities; full comparison prevents a false hit.

`INDEX_BITS` changes the line count to `2**INDEX_BITS`; line and word sizes stay
fixed. Only practical configurations should be instantiated. The documented
range is 1..27, but the upper bound describes address decomposition, not a
feasible register-array size. Default results use six unless explicitly marked.

## Logical storage and hardware implications

Each default line stores:

| Field | Bits/line | Default total |
|---|---:|---:|
| Data | 128 | 8,192 |
| Full line identity | 28 | 1,792 |
| Valid | 1 | 64 |
| Prefetched, not yet consumed | 1 | 64 |
| **Total** | **158** | **10,112 bits** |

This excludes predictor, request/response registers, controller and counters.
Removing redundant index bits could save `64*6 = 384` logical bits; that is not
a measured area saving. The synchronous reset clears the arrays, and lookup is
combinational. This style is suitable for a small register/distributed-memory
baseline, not evidence of FPGA block-RAM inference or timing closure. A BRAM
conversion would require synchronous lookup and a different reset/data path.
Generic synthesis statistics are reported separately from device resources.

## Interface contract

| Channel | Payload | Transfer condition |
|---|---|---|
| CPU request | `cpu_req_addr[31:0]` | `cpu_req_valid && cpu_req_ready` |
| CPU response | `cpu_rsp_data[31:0]` | `cpu_rsp_valid && cpu_rsp_ready` |
| Memory request | aligned `mem_req_addr[31:0]` | `mem_req_valid && mem_req_ready` |
| Memory response | `mem_rsp_data[127:0]` | `mem_rsp_valid && mem_rsp_ready` |

All transfers occur on a rising edge. A producer holds valid and payload stable
while valid is high and ready is low. Every accepted CPU request receives exactly
one response in order, unless shared reset cancels the work. The memory returns
one response per accepted request and no unsolicited responses. A response made
available immediately with a request must be held until the cache enters WAIT
and asserts ready; no combinational-response shortcut is assumed.

Reset is synchronous active high. It clears control, output validity, counters
and all resident metadata/data. Cache and memory reset together; cache-only
reset followed by an old memory response is unsupported. `prefetch_enable`
controls new speculative selections, not cancellation of a selected transaction.
Counters are 32-bit and wrap; Level 5 run limits and wider elapsed-cycle
accumulators do not remove the hardware counter limitation.

## Demand, refill and response behavior

1. A request is accepted only if no demand is pending, the response register has
   room (or is being consumed), reset is inactive and no fill occurs that edge.
2. A hit registers the selected word. A response can be consumed at the next
   clock edge; a consumed response can be replaced with a new hit response on
   the same edge. First demand use of a prefetched-marked line clears the marker.
3. A miss saves the entire byte address and blocks new CPU acceptance. IDLE
   rechecks the line before selecting a demand transaction.
4. SEND holds the aligned line-read request until memory accepts it. WAIT holds
   the transaction until its full line response is accepted.
5. Every fill updates the indexed data/identity/valid bit. A demand fill creates
   the CPU response and releases the pending demand. A speculative fill sets its
   prefetched marker but does not create a CPU response.

Cache hits can proceed during speculative SEND/WAIT, **until a demand miss is
queued**. They are blocked on a fill edge. This is not a nonblocking cache that
serves arbitrary younger hits around an outstanding demand miss.

## Arbitration and late demand recheck

At IDLE, a pending demand has priority over a candidate, and an accepted CPU
request prevents a simultaneous speculative selection. Once SEND asserts a
memory request, even an **unaccepted** prefetch is nonpreemptible. Replacing its
address during backpressure would violate the ready/valid contract. Thus demand
priority means priority at selection, not unconditional absence of interference.

A demand for the in-flight prefetch is initially counted as a miss because the
line was not resident at acceptance. After the speculative fill, IDLE rechecks
its saved line and returns it without issuing a duplicate memory read. This is
late prefetch consumption, not a timely hit.

## Known limitations and Phase 2 boundary

Phase 1 deliberately retains one direct-mapped cache, one global stride history,
one replaceable candidate slot and one outstanding transaction. It implements
neither feedback throttling nor a separate speculative buffer. Wrong predictions
can waste bandwidth and evict hot lines. A greater distance alone cannot create
memory bandwidth or transaction parallelism. Writes, coherence, address
translation, exceptions, real DDR timing and FPGA integration are separate work.

The [Level 5 comparisons](../level5/README.md) must show negative cases alongside
regular-stream gains. Phase 2 can add buffer isolation and measured admission
feedback on a different branch; its results must be compared against this exact
Phase 1 resource/metric contract.
