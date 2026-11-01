# Two pass engineering audit

The upgrade starts from Phase 1 commit `7851de10f6311847ded4ff04640c678ba3999437`. Phase 1 source, measurements and presentation stay unchanged. The first pass diagnoses the baseline and sets experiments. The second pass independently challenges the implemented upgrade, results and claims.

## First pass questions

1. What can the hardware observe? Address regions, repeated deltas and completed prefetch outcomes are observable. Tensor identity, future accesses and CDM choice probabilities are not inputs to this interface.
2. Which defect matters first? A speculative fill can overwrite a hot demand line. Isolating speculative data addresses that mechanism directly.
3. Does context add value beyond extra storage? Compare global stride with a buffer, region stride with a buffer, outcome gating, and a demand victim buffer using the same additional 32 data bytes.
4. Does the benchmark reflect more than favorable streams? Include complete numerically checked kernel read orders, authentic corpus driven lookup IDs, held out seeds, region boundaries, conflict, random and phase transitions.
5. Are timing and cost claims justified? The serial driver and single outstanding transaction establish subsystem latency behavior. They do not establish HBM bandwidth, physical DRAM timing, watts or full inference acceleration.

## Evidence gates

| Layer | Required evidence |
|---|---|
| Trace source | Algorithm or source URL, license, hash, split, deterministic layout and numeric checks |
| Architecture | Bit accounting, legal storage placement and an equal extra data control |
| Prediction | Exact state updates, suppression and recovery, bounds and failure cases |
| RTL | Independent data checking under reset and arbitrary stalls, fate conservation and synthesis |
| Performance | Identical replay conditions, frozen validation selection, held out results and regressions |
| Communication | Every headline traced to a file, formula or primary source, with measured and analytical evidence distinguished |

## Second pass procedure

Reviewers exchange ownership: a reviewer who did not implement the RTL checks its protocol and counters; a reviewer who did not build the benchmark recomputes metric and selection arithmetic; research checks novelty, dataset quality and company relevance against primary sources. Root reconciles findings, fixes confirmed issues and reruns affected checks. An unresolved limitation remains visible rather than receiving a pass label.

The final audit records actual commands, counts, source locations and remaining limits. It uses an unofficial engineering rubric and makes no prediction about judging outcomes.
