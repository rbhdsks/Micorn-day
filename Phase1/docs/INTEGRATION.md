# Integration contract

The testbench acts as a request source, not a CPU executing instructions. The RTL is a read-only subsystem; the memory model is simulation-only.

| Interface | Contract |
|---|---|
| CPU request | 32-bit byte address, aligned four-byte reads; accepted at rising-edge valid AND ready |
| CPU response | One ordered 32-bit word per accepted request; hold valid/data until accepted |
| Memory request | Aligned 16-byte line read, one selected transaction at a time; hold valid/address until ready |
| Memory response | Exactly one 128-bit line for each accepted request; hold until cache ready |
| Reset | Synchronous active high; reset both endpoints and cancel their old operations together |
| Memory contents | Immutable while cached; no writes, coherence, protection, errors or virtual translation |

A zero-combinational-latency memory may present a response immediately, but must hold it until the cache enters WAIT and asserts ready. Unsolicited or stale post-reset responses are unsupported.

A miss occupies the single demand slot and blocks new CPU request acceptance. Cache hits can complete while a speculative transaction is selected/in flight, until a demand miss queues. Lookup acceptance is blocked on a memory-fill edge. A response can be replaced by a new hit only when the previous response is accepted on the same edge.

Demand wins when selecting a transaction in IDLE. A speculative request already in SEND is nonpreemptible even if memory has not accepted it; replacing its address under valid AND NOT ready would violate the contract. A pending demand rechecks the cache after a speculative fill to avoid duplicate reads for the same line.

Default arrays use full 28-bit line identities and combinational reads. Resetting all data and using asynchronous lookup favors a register/distributed-memory implementation; a synchronous block-RAM version requires a latency/control redesign. Generic synthesis is a logical check, not target mapping, timing closure, power or FPGA validation.

The no-prefetch reference disables speculation at runtime and retains the compiled predictor logic. The reported policy synthesis counts are not an area comparison with a separately minimized cache-only hardware module.
