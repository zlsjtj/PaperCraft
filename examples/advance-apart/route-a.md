# Keeping the Required Neighbour Value While Workers Advance Apart

*Constructed DEMO for editorial development. All mechanisms and values are supplied teaching material; no experiment was run.*

## Abstract

A diffusion worker can finish its interior work before its neighbour, yet still need that neighbour's value for a particular step. We replace a wait at every global barrier with a local condition: every required edge value must match the consumer's epoch and step and remain available until released. Two incoming slots let a producer prepare another value without replacing one still in use. In six constructed cases, this guarded configuration meets the final-error requirement throughout. Time falls most under uneven work or delayed delivery, but increases in the smallest balanced case; memory rises in every case. The change concerns when existing boundary updates may proceed, not a new stencil.

## Introduction

The inherited solver already partitions a rectangular field into four patches and schedules asynchronous work. Its baseline, B, nevertheless waits at a global barrier after each step. The proposed configuration, G, removes that wait without allowing a boundary update to consume whichever neighbour value arrived last. This is the engineering problem: workers may progress separately, but an update still needs the right inputs and those inputs must survive until consumption.

Consider W0 about to update step 17. W1 has sent step 17 and is preparing step 18, while a late step-16 packet remains queued. Selecting the newest arrival cannot identify the required input. Checking a label also cannot preserve an input that another write is allowed to replace. G therefore couples selection of the required value with permission to reuse its storage. The evaluation asks whether the resulting overlap is useful after accuracy and storage costs are included.

## Method

Each interface in G has two slots holding copied neighbour edge values, an epoch, a step and a ready flag. W0 reads only a ready slot matching its required pair; every applicable edge neighbour must provide a match. Step 16 cannot serve step 17, and a matching step from an earlier partition epoch is likewise ineligible. Ghost values are copies, not additional physical cells; diagonally touching patches exchange nothing.

The step-17 slot remains live until W0 acknowledges release. W1 can use a free slot for a subsequent value, but must wait if both are live. Thus G permits bounded overlap while retaining local waiting. Missing matching input beyond the existing timeout sends all workers back to the last completed barrier snapshot to rerun using B. Partial G progress is not completed work. Obsolete-packet disposal is unspecified.

## Results and conclusion

The paired comparisons retain the same field, grid, partition plan, precision and 2,000 steps within each case. Both B and G meet the fixed maximum relative final-field error of 1e-6 against the serial stencil. G reduces elapsed time by 16.8–23.6% in the two skew cases and by 13.4–14.9% under clustered delays or epoch migration. Balanced cases give a different judgment: the large grid improves by 2.3%, whereas the small grid slows by 5.8%. Extra peak memory is 9 MiB for small grids, 38 MiB for large grids and 24 MiB for the remaining cases.

Unchecked replacement, U, is faster in all six cases but fails the error requirement throughout. It shows why raw time is insufficient; it does not isolate the benefit of either G check. Separate constructed traces exercise old-epoch rejection (12/12), full-slot waiting (12/12) and snapshot fallback (4/4), with successful B recovery but no restart timings. These are branch checks, not reliability trials. With no repeats, component ablations or prior-art search, this DEMO supports a conditional whole-design comparison, not physical performance or novelty.
