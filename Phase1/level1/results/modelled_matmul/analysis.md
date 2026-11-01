# Modelled matrix-multiplication analysis

## Provenance and assumptions
Generated locally by `generate_matmul_trace.py`. Algorithm-level addresses, not a captured CPU/GPU trace. Configuration: M=16, K=16, N=32; row-major four-byte elements; analysis line size 64 bytes. C initialisation is included. Every multiply-accumulate models A read, B read, C read and C write, without register reuse. No clocks or physical addresses are modelled.

## Measured observations
- Both orders passed an independent dot-product reference check and produced identical result matrices.
- Each trace contains 33,280 address observations.
- ijk touches 80 lines; ikj touches 80 lines. Equal footprint does not imply equal miss rate.
- B compute-read byte deltas (ijk, top four): [(128, 7680), (-1916, 496), (-2044, 15)].
- B compute-read byte deltas (ikj, top four): [(4, 8176), (-2044, 15)].
- The inner-loop B step is N*4 = 128 bytes for ijk and 4 bytes for ikj (where an inner loop has at least two iterations). Boundary transitions also occur.

## Design implications to investigate
Sequential/next-line fetching is a candidate for contiguous streams; a stride predictor is a candidate for regular non-unit streams. Interleaving can hide either pattern from a global predictor. C reuse and A repetition need cache evaluation, not an assumption of hits. Compare policies on the complete stream with explicitly defined write handling and identical resources.

## Limits and next steps
No hit rate, prefetch accuracy, bandwidth benefit, or speedup has been demonstrated. Add a baseline cache model next; hardware timing and actual workload validation follow later. Official acceptance of these modelled traces is unconfirmed. Figures and per-order raw traces, metadata, numeric outputs, and summaries are stored alongside this report.
