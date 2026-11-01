# Level 3: Phase 1 prefetch algorithm

Phase 1 compares no prefetch, next-line and a confidence-qualified signed-stride
policy using the [same cache/controller](../level2/cache_specification.md).
`PREFETCH_POLICY=1` selects stride; `PREFETCH_POLICY=2` selects next-line.
`prefetch_enable=0` suppresses new speculative selections for the cache-only
baseline. It does not cancel a selected transaction.

This is a hardware heuristic, not a neural predictor. The input is an accepted
32-bit demand address. There is no instruction PC, stream ID or layer hint.
Source: [cache controller](../level4/rtl/ai_cache.sv) and
[stride predictor](../level4/rtl/stride_prefetcher.sv).

## Decisions the algorithm must define

| Decision | Signed-stride policy | Next-line reference |
|---|---|---|
| Trigger | Accepted demand accesses, hits or misses; train only when the line differs from the last observed line | Accepted demand accesses, hits or misses; propose only for a new observed line |
| Address units | 28-bit 16-byte line identity | Same |
| Distance | One detected stride ahead | One line ahead |
| Degree | At most one candidate per qualifying observation | At most one candidate per distinct-line observation |
| Confidence | Two matching nonzero deltas; uses previous confidence >=1 on a match | No stride training threshold |
| Filtering | Reject address-space overflow/underflow; controller discards a resident candidate at selection | Reject prediction beyond the highest line; same resident suppression |
| Priority | Pending/accepted demand blocks new speculation; selected SEND/WAIT prefetch cannot be preempted | Same controller |
| Insertion | Prefetch fills replace the indexed ordinary cache line and set a marker | Same |
| Resource limits | One global history, one replaceable candidate slot, one memory transaction | One last-line record for repeat suppression, same slot/controller |

The no-prefetch baseline still uses identical demand lookup, refill, readiness,
DRAM model and workload timing. A performance comparison changes policy, not
cache geometry or memory service assumptions.

## Predictor state and arithmetic

| State | Width | Meaning |
|---|---:|---|
| `seen` | 1 | At least one distinct line has been recorded |
| `last_line` | 28 | Last accepted distinct demand line |
| `stride` | signed 29 | Latest observed nonzero line delta |
| `confidence` | 2 | Saturating repeated-delta count, 0..3 |
| `candidate_valid` | 1 | Clocked candidate pulse |
| `candidate_line` | 28 | Proposed line identity |

The stride predictor has 60 bits of history (`1+28+29+2`) and 29 output-register
bits. This is a logical state count, not a gate/LUT/area measurement. The
controller adds its own pending-candidate address/valid state.

Zero-extend each line identity before signed subtraction. Two 28-bit unsigned
line values have a difference in `[-(2^28-1), +(2^28-1)]`, fitting signed 29 bits.
The sum `line + stride` is signed 30 bits. Issue only when
`0 <= predicted < 2^28`, then reconstruct the aligned byte address by appending
four zero bits. This prevents top/bottom wraparound.

Confidence is **pattern repetition**, not probability, calibrated accuracy or
feedback from whether a prediction was used. Although it saturates at three,
the current issue threshold does not change between confidence two and three.

## Stride pseudocode

All right-hand state values below denote values before the current clock edge.
The candidate is clocked; it is not an immediate memory fill.

```text
on reset:
    seen = false
    last_line = 0
    stride = 0
    confidence = 0
    candidate_valid = false
    candidate_line = 0

on each non-reset clock:
    candidate_valid = false
    if demand_was_accepted and (not seen or current_line != last_line):
        if not seen:
            stride = 0
            confidence = 0
        else:
            delta = signed(current_line) - signed(last_line)
            if delta == stride and delta != 0:
                predicted = signed(current_line) + signed(stride)
                if enabled and old_confidence >= 1 and 0 <= predicted < 2^28:
                    candidate_line = predicted
                    candidate_valid = true
                confidence = min(old_confidence + 1, 3)
            else:
                stride = delta
                confidence = 1
        seen = true
        last_line = current_line
```

Example in line units: `100,104,108` contains two +4 deltas and proposes `112`.
The byte stride is 64 bytes with a 16-byte line. `30,20,10` proposes zero; a
subsequent predicted negative line is suppressed. `100,100,100,104,108` trains
like `100,104,108`: word-level accesses within a line do not overwrite the useful
line stride with zero.

For Nitesh's N=32 row-major matrix model, the B inner-loop stride in `ijk` is
128 bytes, or eight Phase 1 lines. In `ikj`, B's four-byte step often remains
within the current line. Loop boundaries, A accesses and C accesses break the
single-stream sequence; a clean per-operand graph does not prove that this
global predictor sees those same patterns.

## Next-line pseudocode

```text
on accepted demand for a new observed line:
    remember the line for adjacent-repeat suppression
    if enabled and current_line < 2^28 - 1:
        propose current_line + 1
```

Unlike stride, this reference can propose after its first line. That is an
intentional startup difference and should appear in short-burst comparisons.
It need not be best for larger strides: after line 100 it predicts 101 even if
the actual next line is 108. It is a genuine RTL baseline, not an instantaneous
Python policy result.

## Candidate scheduling and request control

The predictor's registered output is advisory. The controller captures a
candidate into one pending slot; newer predictions may replace queued ones.
When IDLE, it first resolves a pending demand. Only with no accepted/pending
demand can it take the candidate, check residency and select a speculative read.
SEND asserts a stable aligned address until accepted; WAIT receives one line.
The controller cannot launch a second memory request during either state.

A candidate already represented in cache is discarded at selection. A selected
prefetch cannot be selected again in parallel because there is only one memory
transaction. A repeated queued candidate is checked after the transaction fills,
so a resident duplicate is discarded. A queued demand is rechecked after a
speculative fill, preventing a duplicate demand fetch for that now-resident line.
There is no multi-entry duplicate CAM or multi-outstanding request table.

A candidate may be dropped when a replacement arrives on the same edge as
consuming the old slot in the retained baseline scheduling. It is advisory work:
this loses an opportunity, not the response to an accepted CPU request. Such
queue-event behavior must be kept visible when changing the implementation.

Training continues while `prefetch_enable` is low, but output/admission is
suppressed and the queued candidate is cleared. An already selected SEND/WAIT
transaction may still finish after disable. An unrelated demand arriving after
speculative selection can wait behind it even if memory has not accepted the
prefetch; changing a blocked valid address would break ready/valid stability.

## Timeliness and accounting

A correct prediction helps most when it completes before demand acceptance.
If the line was marked prefetched and already resident, its first demand hit is
**timely useful**, and the marker clears. If demand arrived during its transfer,
it is initially a miss, then consumes the line on the controller recheck: this
is **late useful**. It may shorten the stall without becoming a hit.

An unconsumed marked line evicted from the cache is **unused evicted**. A marked
line remaining at the end is **resident unconsumed**, not a confirmed eviction.
At quiescence:

```text
issued prefetches = timely useful + late useful + unused evicted + resident unconsumed
```

Hardware `stat_pf_useful` measures timely consumption only. Complete late and
resident fate accounting in Phase 1 comes from the verification bench; do not
present it as additional implemented hardware counters. “Consumed accuracy” is
`(timely + late) / issued`, with zero issued reported as not applicable. It is
finite-window consumption, not an exact-next-address prediction probability.

The memory has one outstanding transaction. Raising distance alone cannot
increase its sustainable bandwidth or overlap arbitrary independent misses.
There must be enough useful lead time; compute gap, request-driver spacing and
memory service all affect observed gains.

## Expected help, failure and Phase 2 scope

| Access behavior | Expected outcome to test | Failure mechanism / caveat |
|---|---|---|
| Long regular positive or negative line stride | Stride learns after two equal deltas | Startup and final unused prediction overhead remain |
| Dense contiguous words | Same-line filtering retains the line pattern | Baseline already benefits from spatial hits; speedup need not track hit-rate gain |
| Sequential stream | Next-line starts earlier; stride catches up after training | Which is faster depends on timeliness and startup length |
| Several interleaved streams | Global history may fail to qualify | Distinct strides and even separate regular streams can overwrite history |
| Three-line bursts | Stride may predict exactly when a burst ends | Additional traffic without useful consumption |
| Random or changed phases | Few repeated deltas often suppress predictions | Accidental repetitions can still cause traffic or pollution; one seed proves little |
| Reused hot lines plus wrong predictions | Demand correctness remains intact | Direct-map speculative fills can cause extra misses; include the pollution regression |
| Little compute gap / slow memory | Predictions can arrive late | A useful prediction does not imply a timely cache hit |

Phase 1 does not claim dynamic usefulness feedback, bandwidth throttling,
adaptive distance, multistream/PC indexing or a separate prefetch buffer. Those
are potential Phase 2 upgrades. First show the baseline's failure cases and
compare no-prefetch, next-line and stride fairly using the [Level 5
methodology](../level5/README.md).
