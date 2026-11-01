# Actual workload analysis — pending input

No official workload trace has been supplied. Synthetic tooling examples do not establish workload behaviour.

## Input provenance and schema

Pending: workload/model, input, trace generator, source, redistribution conditions, address units, operation types, request sizes, timestamps, PC/stream fields, trace ordering, and sampling/truncation details.

## Analysis assumptions

Pending validation: cache-line size, whether observations are reads only, whether a request can cross a line, and how multiple request streams are interleaved.

## Measurements and evidence

Pending real trace. Include working set, line deltas, reuse, phase/window comparisons, and limitations. Do not infer cache misses from unique-line counts or reuse gaps alone.

## Design implications

Pending evidence: compare sequential, fixed-stride, and irregular regions; choose candidates for software-model evaluation. Do not select the final predictor solely from synthetic tests.

## Available preliminary experiment

A modelled matrix-multiplication experiment is now available in `matmul_analysis.ipynb`, with measured conclusions in `results/modelled_matmul/analysis.md`. This is a separate, clearly labelled starting example; it does not replace the pending official/captured workload analysis above.
