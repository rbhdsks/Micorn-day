# Level 2: cache architecture

- [Cache specification and rationale](cache_specification.md)
- [Block diagram](cache_architecture.svg)
- [Editable Mermaid source](cache_architecture.mmd)

These describe the Phase 1 implementation. The default is a 1 KiB read-only,
direct-mapped cache with 16-byte lines. Choices, address calculations, interface
rules, storage accounting and limitations are explicit; they are not presented
as organizer-mandated or optimal for all AI workloads.
