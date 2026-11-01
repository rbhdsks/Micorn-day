# Phase 1 figures

Each figure is supplied as PNG, PDF and SVG. Figures 01-07 derive from retained RTL/trace evidence. Figures 08-09 separately reproduce CDM illustration arithmetic and analytic storage.

## Completion speedup depends on access pattern; all 13 workloads, identical cache and timing.

![Completion speedup depends on access pattern; all 13 workloads, identical cache and timing.](01_speedup.png)

Evidence: measured RTL.

## Demand hit rate is not execution speedup; all 13 workloads, identical cache and timing.

![Demand hit rate is not execution speedup; all 13 workloads, identical cache and timing.](02_hit_rate.png)

Evidence: measured RTL.

## Response availability includes late-prefetch benefits; all 13 workloads, identical cache and timing.

![Response availability includes late-prefetch benefits; all 13 workloads, identical cache and timing.](03_latency.png)

Evidence: measured RTL.

## Traffic ratio; pollution case shown separately to preserve the scale.

![Traffic ratio; pollution case shown separately to preserve the scale.](04_traffic.png)

Evidence: measured RTL.

## Stride-prefetch outcomes conserve after natural quiescence.

![Stride-prefetch outcomes conserve after natural quiescence.](05_prefetch_fates.png)

Evidence: measured RTL.

## 320 demanded reads, four distinct demanded lines; all data correct despite the slowdown.

![320 demanded reads, four distinct demanded lines; all data correct despite the slowdown.](06_pollution.png)

Evidence: measured RTL.

## Unique touched lines are a footprint measure, not a cache-capacity requirement.

![Unique touched lines are a footprint measure, not a cache-capacity requirement.](07_workload_footprint.png)

Evidence: measured RTL.

## Supplied illustrative factors; not fitted models and not cache measurements.

![Supplied illustrative factors; not fitted models and not cache measurements.](08_cdm_probabilities.png)

Evidence: recalculated notes illustration.

## Analytic tensor storage excludes optimizer, gradients, data and temporary matrices.

![Analytic tensor storage excludes optimizer, gradients, data and temporary matrices.](09_cdm_storage.png)

Evidence: analytic storage.
