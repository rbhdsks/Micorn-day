# Level 3 Prefetch strategy

The implemented predictor observes accepted demand addresses. It learns signed line strides and proposes one future line. A separate next-line RTL policy provides the comparison. The cache controller decides whether and when a candidate becomes a memory request.

Open [the runnable walkthrough notebook](prefetch_walkthrough.ipynb) to inspect the state one observation at a time. The [complete strategy specification](prefetch_strategy.md) covers the hardware contract and failure modes.

## Run the starting example

From `Phase1/`:

```sh
python3 level3/explain_prefetch.py --demo --policy stride
python3 level3/explain_prefetch.py --lines 100 104 108 --json
PYTHONPATH=level3 python3 -m unittest discover -s level3/tests -v
```

The explanatory model reproduces predictor arithmetic and history updates. It does not model cache fills, backpressure, DRAM timing or speedup. The RTL in [Level 4](../level4/README.md) supplies those measurements.

## Decisions in the implemented baseline

| Decision | Stride policy | Next-line reference |
|---|---|---|
| Trigger | Accepted demand hit or miss, distinct line only | Same |
| Distance | One detected stride ahead | One line ahead |
| Degree | At most one candidate | At most one candidate |
| Confidence | Two equal nonzero deltas | No training threshold |
| Filtering | Bounds check, then resident suppression at selection | Upper bound, then resident suppression |
| Priority | Queued/accepted demand wins at selection | Same controller |
| Insertion | Ordinary direct-mapped cache fill | Same |
| History | One global last line and signed stride | Last line for repeat suppression |

## Worked example

| Accepted line | Delta | Confidence after update | Candidate |
|---:|---:|---:|---:|
| 100 | unavailable | 0 | none |
| 104 | +4 | 1 | none |
| 108 | +4 | 2 | 112 |

The matching-delta decision uses the **previous** confidence. Repeated words within one line do not train a zero stride. Negative strides work, and predictions outside the 28-bit line space are suppressed.

```text
if new distinct demand line:
    delta = current - previous
    if delta matches stored nonzero stride:
        if old confidence >= 1 and address is in range: propose current + stride
        saturating increment confidence
    else: replace stride and set confidence = 1
```

## Why correct predictions can still fail

A prediction that arrives after demand acceptance is late. It can shorten waiting without becoming a cache hit. One outstanding memory transaction limits overlap. A selected prefetch is nonpreemptible under ready/valid, so later demand may wait behind it.

Multiple streams overwrite global history. Three-line bursts may end just when the predictor qualifies. Speculative direct-map fills can evict hot demand lines. [Measured negative cases](../level5/results/reference/report.md) remain part of the baseline.

## Continue the work

Use the [state model](explain_prefetch.py), [RTL](../level4/rtl/stride_prefetcher.sv) and [policy tests](tests/test_predictor_model.py) together. Change one decision at a time and compare all policies under the same cache and timing. The separate buffer, feedback and proposed CDM policy connection remain research/Phase 2 work, not measured Phase 1 RTL features.
