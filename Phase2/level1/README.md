# Level 1: dataset quality and numerically checked access generation

This suite separates three evidence classes. A realistic input source improves input provenance; it does not turn assigned addresses and replay gaps into captured processor execution.

| Class | Cases | Role and limit |
|---|---:|---|
| Inherited Phase 1 diagnostics | 13 | Same address/gap sequences; verifies baseline equivalence and retains negative cases |
| Instrumented complete numeric kernels | 24 | Four families × three documented shape/layout seeds × two gaps; small scalar input-read microbenchmarks |
| Authentic WikiText input, modelled embeddings | 6 | Three published corpus splits × two gaps; real text order, assigned embedding IDs/layout/timing |
| Boundary/interference stress | 12 | Three patterns × four gap/latency conditions; deliberately adversarial, not representative frequencies |

## Run

```sh
# From repository root. Source corpus stays in ignored Phase2/build/data.
python3 Phase2/level1/fetch_corpus.py --download
python3 Phase2/level1/generate_suite.py
PYTHONPATH=Phase2/level1 python3 -m unittest discover -s Phase2/level1/tests -v
```

`--no-corpus` generates the 49-case offline subset, which is a different suite and must be labelled that way. The complete published evaluation uses 55 cases. [The generator](generate_suite.py) records configs, numeric checks, source hashes, row counts and splits in its manifest. Compact generated trace rows are retained with the results. Raw source text and full per-request replay samples belong under ignored build directories.

## Kernel mathematics and instrumentation

For tiled GEMM, compute each output `C[i,j] = sum_k A[i,k]B[k,j]`, traversing blocked `ii,jj,kk,i,j,k` loops with tile size four. The input trace records both operand reads at each multiply. An uninstrumented sum-of-products reference checks every output. M/N/K differ across seeds 11/101/202, and assigned operand bases vary cache-set alignment. All three cases perform 768 scalar input reads; that count does not imply equal behavior.

For valid 1D cross-correlation, `Y[o,x] = sum_c sum_z X[c,x+z]W[o,c,z]`; for depthwise cross-correlation, `Y[c,x] = sum_z X[c,x+z]W[c,z]`. Stride is one and padding zero. Channel counts, lengths and widths are declared per case. A separate uninstrumented expression checks each calculated output. These tests establish the generator's arithmetic and access count, not real-model accuracy.

Embedding pooling computes `Y[d] = sum_t E[id_t,d]`. The synthetic hot-index family samples 96 indices from 512 rows with finite rank weights proportional to `(rank+1)^(-1.15)`, reading eight words per embedding. This is an explicit synthetic skew, not a measured recommendation popularity distribution.

All kernels execute complete small numeric operations while logging their immutable input reads. Output writes, instruction fetches, cache coherence, virtual-to-physical translation and surrounding runtime traffic are excluded. RTL replay checks its address-derived memory words; it does not run the Python tensor arithmetic. Matrix and convolution data values do not affect these address-only policies.

## Authentic input and its modelling boundary

The corpus is the [official Salesforce WikiText release](https://huggingface.co/datasets/Salesforce/wikitext), configuration `wikitext-2-raw-v1`. The [source paper](https://arxiv.org/abs/1609.07843) describes the language modelling corpus. We fetch the first 100 rows of each published train/validation/test split through the dataset viewer API, require exact concatenated UTF-8 content hashes and use the first 256 whitespace tokens. The live API endpoint is not a revision-pinned archive; checksum verification rejects silent content drift. The source card revision and all hashes are recorded.

The mapper preserves case and punctuation, hashes each UTF-8 whitespace token with BLAKE2b-64, interprets it as an unsigned big-endian integer and reduces modulo 65,536. This fixed mapping requires no vocabulary fit on held-out data. Each ID selects an eight-word row at an assigned 32-bit base. The manifest counts unique tokens, unique IDs and collisions. This is a bounded embedding-access experiment, not an actual language-model tokenizer, trained embedding table or inference run. Frequent-word reuse is authentic to the sampled input; address placement and collision behavior are imposed by the mapper.

Upstream dataset metadata names CC BY-SA 3.0, while the pinned dataset card's prose links CC BY-SA 4.0. We record that upstream inconsistency instead of inventing a license version. The source text is not redistributed. Cite Stephen Merity, Caiming Xiong, James Bradbury and Richard Socher, *Pointer Sentinel Mixture Models*, 2016, together with the source dataset card. No Salesforce, Wikipedia or dataset-author endorsement is implied.

MovieLens 100K was considered. Its [primary README](https://files.grouplens.org/datasets/movielens/ml-100k-README.txt) distinguishes research use, redistribution and commercial-use conditions. It is not downloaded or included in this evaluation. This is a source-selection decision, not a conclusion about permissions for a particular event.

## Split and sampling limits

Kernel seed 11 and WikiText's published train input form the validation split. Seeds 101/202 and the published validation/test input form the held-out split. These labels concern this hardware-policy experiment, not language-model training. All policies start cold for each trace. The two gaps replay the same address sequence and are correlated conditions. Kernel seeds change documented shapes/layouts, while embedding seeds additionally change index samples; they are not independent draws from a production application population.

The suite deliberately retains same-region alternating streams, strides that leave a 4 KiB region before confidence can build, and mixed regular/waste regions. Four region trackers and a global outcome gate can fail on these patterns. Do not remove them to improve a headline score. The finite suite supplies exact counterexamples and conditional gains; it cannot establish universal workload representativeness.
