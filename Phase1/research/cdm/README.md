# Low rank context dependent choice research

This chapter reproduces the mathematics in Nitesh Kumar Shah's supplied *Learning from Comparison Data* draft, sections 4.4-4.6, and proposes a connection to policy selection. CDM is **not implemented in the cache RTL**. Its choice probabilities are not cache hit probabilities or prefetch accuracy.

## Run and inspect

```sh
# From Phase1
python3 research/cdm/cdm_reference.py
PYTHONPATH=research/cdm python3 -m unittest discover -s research/cdm/tests -v
```

Open [the executed walkthrough](cdm_walkthrough.ipynb), [calculated example probabilities](results/chosen_probabilities.csv) or [storage calculations](results/parameter_storage.csv).

## The model and the correct formulas

For available alternatives S, target x receives the effects of the **other available alternatives**:

$$s_x(S)=\sum_{z\in S\setminus\{x\}}u_{xz},\qquad P(x\mid S;U)=\frac{\exp(s_x(S))}{\sum_{y\in S}\exp(s_y(S))}.$$

The low-rank parameterization assigns a target vector and context vector to each alternative:

$$u_{xz}=t_x^\top c_z\quad(x\ne z),\qquad M=TC^\top,\qquad T,C\in\mathbb R^{n\times r}.$$

The rank bound applies to M. Diagonal entries are excluded from scores, and zeroing that diagonal can increase matrix rank. Target/context interactions need not be symmetric. The factors are learned parameters, not observed workload features.

For observations (S_k,y_k), the mean negative log likelihood is

$$\overline{\mathcal L}=-\frac1K\sum_{k=1}^K\log P(y_k\mid S_k).$$

Compute probabilities with a shifted softmax, subtracting the largest available score before exponentiation. The reference implementation does this to prevent overflow.

## Reproduced illustration from the notes

The supplied Chai/Coffee/Juice initial factors yield the following independently recalculated mean NLL values on the same six observations:

| Factor rank | Mean NLL |
|---|---:|
| 1 | 0.750970 |
| 2 | 0.742501 |
| 3 | 0.753631 |

These compare hand-chosen **initial factors**. They are not trained-model results and do not establish that rank 2 generalizes better than rank 3. More capacity does not guarantee a better arbitrary initialization. The reference CSV retains each chosen-item probability.

## Storage and identifiability

A dense implementation stores n squared entries. The factors store 2nr entries. Float64 parameter-only storage is 8N / 2^20 MiB. At n=5000, that is 25,000,000 dense entries versus 10,000 / 20,000 / 30,000 entries for ranks 1 / 2 / 3.

Stored-entry counts are not identifiable degrees of freedom. The full CDM has n(n-1) off-diagonal values and one common-shift gauge under a sufficiently rich choice-set design. Restricted observations can leave further nonidentifiability. Factorizations also have change-of-basis ambiguities. Do not call 2nr identifiable parameters or equate small parameter storage with small total process memory.

The notes' dense training implementation can materialize quadratic intermediate matrices. Linear factor storage therefore does not prove linear runtime or a proportional reduction in process RSS. The reported large PyTorch timing experiments in the notes were **not rerun** here; the repository's CDM figures show reproducible arithmetic and analytic storage only.

## A proposed cache connection

Use a bounded alternative set such as no prefetch, next-line and stride. A selector could learn preferences among available legal policies. That is a research proposal, not the current hardware behavior. Standard CDM models choice-set effects; it does not automatically condition on current miss rate, stride confidence or bandwidth pressure. Workload telemetry would require an explicit contextual extension, for example an additional feature-dependent score term, and separate training/evaluation.

A defensible experiment would label policy outcomes from controlled paired simulations, split by workload/seed/phase, select rank on validation data and reserve held-out tests. Compare against fixed policies and a simpler selector. Record selection NLL/calibration separately from hardware completion-cycle speedup, traffic, timeliness and added implementation cost. Avoid choosing a policy with future trace information at deployment. Exponentials may be unnecessary for argmax selection, but fixed-point score quantization still needs verification.

## Design thinking research plan

The user of the selector needs predictable memory delivery under changing access patterns. The measurable problem is wasted transactions or late delivery. Prototype offline selection first, test on unseen phases and compare its gains with the simpler buffer/feedback upgrade. If it fails to improve paired cycle/traffic outcomes, retain the simpler design. No winning probability or CDM performance benefit is assumed.

## Sources

- Nitesh Kumar Shah, *Learning from Comparison Data*, first draft, 2026, supplied Notes.pdf, sections 4.4-4.6, printed pages 29-46. The private source PDF is not redistributed.
- Arjun Seshadri, Alex Peysakhovich and Johan Ugander, [Discovering Context Effects from Raw Choice Data](https://proceedings.mlr.press/v97/seshadri19a.html), ICML 2019. CDM and its low-rank form are established research.
