# Level 3: prefetch strategy

[Algorithm, state table and pseudocode](prefetch_strategy.md) define every policy
choice: trigger, distance, degree, confidence, filtering, demand priority and
insertion. The document explains timely versus late use, arithmetic bounds,
resource limits and expected failure cases.

Phase 1 includes the existing signed-stride policy and an RTL next-line
reference. Buffer isolation, usefulness feedback and multistream tracking are
reserved for Phase 2.
