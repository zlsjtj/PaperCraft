# Keeping the Required Neighbour Value While Diffusion Workers Advance Apart

*Constructed DEMO for editorial development. All mechanisms and values are supplied teaching material; no experiment was run.*

## Abstract

A diffusion worker may finish its interior work before a neighbour, yet still need that neighbour's value for a particular step. We remove the global barrier while retaining a local requirement: every needed edge value must match the consumer's epoch and step and remain available until released. Two incoming slots let a producer prepare another value without replacing one still in use. In six constructed cases, the guarded configuration meets the fixed final-error requirement throughout. Time falls most under uneven work or delayed delivery, but rises in the smallest balanced case; peak memory increases by 9–38 MiB. The contribution is this change to when existing updates may proceed, not a new numerical stencil.

## Introduction

The inherited solver already partitions a rectangular field into four patches and schedules asynchronous work. Its baseline, B, nevertheless waits at a global barrier after each step. Because producers cannot advance early through that barrier, one incoming buffer per interface suffices. Removing the barrier also removes this protection: independent progress must not replace a value that another worker still needs.

Suppose W0 needs step 17. W1 has sent step 17 and is preparing step 18, while a late step-16 packet remains queued. The latest arrival need not be the required value; even a correctly labelled value is unusable if overwritten before consumption. Configuration G therefore couples selection of the required input with permission to reuse its storage. This keeps a concrete obligation from the barrier-based solver while changing how workers wait. The evaluation asks where that complete change earns a time reduction at higher storage cost.

## Method

Each incoming interface has two slots containing copied neighbour edge values, an epoch, a step and a ready flag. A consumer selects a ready slot only when both labels match its required pair; a boundary update needs matches from every applicable edge neighbour. An earlier partition epoch is ineligible even if its step number matches. Ghost values are copies rather than extra physical cells, and diagonally touching patches exchange nothing.

The step-17 slot stays live until W0 acknowledges release. W1 may use a free slot for another value but must wait when both are live. G thus retains local waiting and bounded storage. If matching input is absent beyond the existing timeout, all workers return to the last completed barrier snapshot and rerun using B; a partial G step is not completed progress. Obsolete-packet disposal remains unspecified.

## Main result and scope

Both B and G satisfy the fixed maximum relative final-field error of 1e-6 against serial execution in all six cases. At each grid size, skew and balanced workloads give different reasons to change the solver. G reduces time by 16.8% and 23.6% under skew, but the balanced small grid slows by 5.8% and the balanced large grid improves by only 2.3%. Migration and clustered-delay cases improve by 14.9% and 13.4%. Added peak memory is 9 MiB on small grids, 38 MiB on large grids and 24 MiB in the other cases. These patterns favor the complete guarded configuration under the supplied uneven-progress conditions without identifying a hardware bottleneck.

Unchecked replacement, U, is faster in every case but fails the error requirement throughout. That comparison rejects ranking the configurations by time alone. It does not show which G component causes the gain. The necessity of matching and protected reuse follows from the step-17 operation above; their separate performance contributions were not measured. Separate branch traces cover old epochs, full slots and fallback, with no reliability estimate or restart timing. All values are constructed, with no repeats or prior-art search to establish physical performance or novelty.
