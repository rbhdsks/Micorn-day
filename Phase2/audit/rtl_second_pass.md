# Second pass RTL and evidence audit

The second pass uses a separately written memory/driver/scoreboard and a metric auditor that does not import the benchmark's metric functions. It is an independent checking method, not external certification or formal proof.

| Review item | Source and executed evidence | Disposition |
|---|---|---|
| FSM ownership | [Typed state and transitions](../level4/rtl/ai_cache_context.sv#L24), [transition monitor](../level4/tb/context_protocol_monitor.sv), independent memory runs | IDLE cannot skip SEND; SEND/WAIT exit only on their exact handshake; all legal edges visited |
| Backpressure | [Ready/valid logic](../level4/rtl/ai_cache_context.sv#L71), [12 concurrent properties](../level4/audit_tests/context_sva.sv) and procedural monitors | Held payloads and one-outstanding bounds pass |
| Reset and unknown payload | [Valid-only reset](../level4/rtl/ai_cache_context.sv#L92), directed SEND/WAIT reset and independent epoch scoreboards |35,982 independent returned responses and18 explicit reset cancellations; no unknown payload escaped a valid response |
| Buffer event ordering | [Promotion](../level4/rtl/ai_cache_context.sv#L119), [fill destination](../level4/rtl/ai_cache_context.sv#L157) | Fill edge excludes acceptance; pending demand excludes a second request; duplicate residency and fate conservation pass |
| Victim control | Swap and demand-eviction paths,13 directed responses plus seeded stress | Same extra32 data bytes, zero prefetch fates, separate buffer-hit classification |
| Signed prediction | [Regional arithmetic and bounds](../level4/rtl/region_stride_prefetcher.sv),31 unit observations | Repeated delta, negative stride, bounds and training/enable behavior pass finite cases |
| Width and driver semantics | Four strict Verilator lint configurations | Explicit width casts added; one narrow alignment-bit waiver reviewed |
| Generic synthesis | [Common-tool cost records](../level4/reference/synthesis.json) | Ten views pass CHECK; mapping heuristic and nonmonotone instrumentation counts disclosed |
| Metrics and source integrity | [Independent result audit](results_second_pass.json) |385 rows,55 pairs,28 aggregates, nearest-rank samples, hashes and selection seal pass |
| MATLAB compatible analysis |18 figure families executed in GNU Octave11.3.0 | All28 validation/holdout aggregate values match Python; native MATLAB execution open |

No confirmed data/protocol defect remains in the exercised legal contract. This statement does not close the following architectural limitations: nonpreemptible selected speculation, region boundary retraining, same-region aliasing, four-entry table pressure, global outcome coupling, advisory candidate loss,32-bit counter wrap, no write/coherence/fault handling and the requirement for shared reset with memory. The FSM default branch is not certified upset recovery.

The first-pass findings on false context/novelty/energy claims are closed by narrower language, primary references and separate CDM research. Dataset breadth improves, but real application capture and realistic concurrency remain open. The resource control exposes a substantive negative result: victim retention dominates the regional variant on held-out aggregate time and traffic. It is retained, not hidden or used to retune the sealed validation choice.

Vivado/xsim, routed timing, board operation, device power, formal proof and coverage closure were not executed. AMD scripts and explicit assumptions prepare those gates without relabelling open gates as passes. Complete local command logs remain under ignored build directories; compact source-hashed evidence is retained in the repository.
