# Keeping the Required Neighbour Value While Diffusion Workers Advance Apart

*Constructed DEMO for editorial development. All mechanisms and values are supplied teaching material; no experiment was run.*

## Abstract

A diffusion worker may finish its interior work before a neighbour, yet still need that neighbour's value for a particular step. We remove the global barrier while retaining a local requirement: every needed edge value must match the consumer's epoch and step and remain available until released. Two incoming slots let a producer prepare another value without replacing one still in use. In six constructed cases, the guarded configuration meets the fixed final-error requirement throughout. Time falls most under uneven work or delayed delivery, but rises in the smallest balanced case; peak memory increases by 9–38 MiB. The contribution is this change to when existing updates may proceed, not a new numerical stencil.

## Introduction

The inherited solver already partitions a rectangular field into four patches and schedules asynchronous work. Its baseline, B, nevertheless waits at a global barrier after each step. Because producers cannot advance early through that barrier, one incoming buffer per interface suffices. Removing the barrier also removes this protection: independent progress must not replace a value that another worker still needs.

Suppose W0 needs step 17. W1 has sent step 17 and is preparing step 18, while a late step-16 packet remains queued. The latest arrival need not be the required value; even a correctly labelled value is unusable if overwritten before consumption. The unchecked configuration, U, removes the same barrier but overwrites its single incoming buffer on arrival and consumes the latest values without testing their step labels. Configuration G instead couples selection of the required input with permission to reuse its storage. This keeps a concrete obligation from the barrier-based solver while changing how workers wait. The evaluation asks where that complete change earns a time reduction at higher storage cost.

## Method

The four equal rectangular patches are arranged W0/W1 above W2/W3; each owns its interior cells and one edge ghost layer. Packing, the finite-volume update formula and partitioning are unchanged. Each incoming interface has two slots containing copied neighbour edge values, an epoch, a step and a ready flag. A consumer selects a ready slot only when both labels match its required pair; a boundary update needs matches from every applicable edge neighbour. An earlier partition epoch is ineligible even if its step number matches. Ghost values are copies rather than extra physical cells, and diagonally touching patches exchange nothing.

The step-17 slot stays live until W0 acknowledges release. W1 may use a free slot for another value but must wait when both are live. G thus retains local waiting and bounded storage. If matching input is absent beyond the existing timeout, all workers return to the last completed barrier snapshot and rerun using B; a partial G step is not completed progress. Obsolete-packet disposal remains unspecified.

![Figure 1](figure1/figure.png)

**Figure 1. Matching and lifetime are separate conditions (constructed DEMO).** The inset preserves the four-patch topology; links denote edge adjacency. The main view follows one W1-to-W0 incoming interface in G. A ready (e, 17) slot feeds W0's step-17 boundary update; a late (e, 16) value cannot be selected. The free second slot illustrates bounded capacity while W1 prepares step 18; the dashed next-write arrow denotes a possible subsequent write, not an observed arrival. Release acknowledgement permits reuse of the consumed slot. Each interface uses the same rules; a complete boundary update still needs all applicable neighbours. The example does not specify obsolete-packet disposal.

## Comparison protocol

Within each case, B, U and G share the initial field, grid, partition plan, precision and 2,000 steps. The reference is serial execution of the same stencil. Eligibility requires maximum relative final-field error at most 1e-6. Elapsed time includes advance, packing, polling, boundary checks and waits, but excludes allocation and setup. Peak memory includes state and message buffers. The fixed criterion preceded these constructed values; no repeats or uncertainty estimates are available.

Balanced and skew cases use 128-by-128 (small) or 512-by-512 (large) grids. Balanced workers have comparable delays; skew cases give W1 more interior work. Migration changes the partition epoch midway on a 256-by-256 grid. Traffic-burst uses that grid size with clustered delivery delays. These categories do not form a time trajectory.

## Where the complete change is useful

Both B and G satisfy the fixed maximum relative final-field error of 1e-6 against serial execution in all six cases. At each grid size, skew and balanced workloads give different reasons to change the solver. G reduces time by 16.8% and 23.6% under skew, but the balanced small grid slows by 5.8% and the balanced large grid improves by only 2.3%. Migration and clustered-delay cases improve by 14.9% and 13.4%. Added peak memory is 9 MiB on small grids, 38 MiB on large grids and 24 MiB in the other cases. These patterns favor the complete guarded configuration under the supplied uneven-progress conditions without identifying a hardware bottleneck.

Unchecked replacement, U, is faster in every case but fails the error requirement throughout. Its errors range from 1.8e-3 to 1.6e-2, while the G error closest to the limit is 9.3e-7 in traffic-burst. That comparison rejects ranking the configurations by time alone. It does not show which G component causes the gain. The necessity of matching and protected reuse follows from the step-17 operation above; their separate performance contributions were not measured.

![Figure 2](figure2/figure.png)

**Figure 2. Time savings and accuracy eligibility must be read together (constructed DEMO).** Each categorical workload has paired time and error displays for all three modes. Time change is 100 × (mode elapsed / B elapsed − 1); negative values mean shorter time. Error uses a logarithmic axis, with the acceptable region shaded through the fixed 1e-6 threshold. Symbols are offset vertically within each row solely for legibility, not as a further measured variable. No lines connect different workloads and no uncertainty intervals are available. All G and B rows qualify; every U row fails. Memory costs and exact values remain in Table 1; injected-timeout episodes are excluded.


*Table 1. All 18 constructed DEMO records. Time covers the advance loop and communication work, excluding setup; error is relative to the serial final field. The fixed accuracy criterion is error ≤ 1e-6.*

| Case | Mode | Elapsed (ms) | Peak (MiB) | Max. relative error | Meets criterion |
|---|---|---:|---:|---:|:---:|
| balanced-small | B | 120 | 82 | 5.0e-8 | Yes |
| balanced-small | U | 108 | 82 | 2.7e-3 | No |
| balanced-small | G | 127 | 91 | 3.2e-7 | Yes |
| balanced-large | B | 480 | 560 | 6.0e-8 | Yes |
| balanced-large | U | 421 | 560 | 1.8e-3 | No |
| balanced-large | G | 469 | 598 | 4.0e-7 | Yes |
| skew-small | B | 244 | 82 | 7.0e-8 | Yes |
| skew-small | U | 188 | 82 | 1.1e-2 | No |
| skew-small | G | 203 | 91 | 5.5e-7 | Yes |
| skew-large | B | 955 | 560 | 7.0e-8 | Yes |
| skew-large | U | 671 | 560 | 8.4e-3 | No |
| skew-large | G | 730 | 598 | 6.0e-7 | Yes |
| migration | B | 710 | 214 | 8.0e-8 | Yes |
| migration | U | 492 | 214 | 1.5e-2 | No |
| migration | G | 604 | 238 | 8.4e-7 | Yes |
| traffic-burst | B | 868 | 214 | 8.0e-8 | Yes |
| traffic-burst | U | 551 | 214 | 1.6e-2 | No |
| traffic-burst | G | 752 | 238 | 9.3e-7 | Yes |

## Branch checks and conclusion

Separate constructed checks refused prior-epoch replay in 12/12 traces and made producers wait on two live slots in 12/12 without overwriting either. Suppressing required packets triggered snapshot fallback in 4/4; the restarted B computations met the final-error requirement, but elapsed times were not recorded. These checks exercise the intended branches rather than estimate reliability. Timeout episodes are absent from the timing table, so the reported gains do not include recovery cost.

The supplied records favor this complete change under uneven work and delayed delivery; the balanced cases retain a slowdown or a much smaller gain. The operation explains why matching and lifetime protection are needed, while the paired outcomes decide the value of the configuration as a whole. There are no repeated measurements, component ablations or prior-art search. The example establishes neither physical performance nor novelty, optimal slot count, universal scaling, a hardware bottleneck or a long-run failure probability.
