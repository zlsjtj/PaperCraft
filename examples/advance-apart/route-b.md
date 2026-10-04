# When Guarded Overlap Is Worth the Additional Storage

*Constructed DEMO for editorial development. All mechanisms and values are supplied teaching material; no experiment was run.*

## Abstract

Removing a diffusion solver's global barrier helps only if the remaining boundary inputs satisfy its accuracy requirement. Across six constructed comparisons, guarded overlap reduces time by 16.8–23.6% under uneven worker loads and 13.4–14.9% under migration or clustered delivery delays. Balanced loads offer less: a 2.3% reduction on the large grid and a 5.8% increase on the small grid. All six guarded records qualify, at extra peak memory of 9–38 MiB. The method retains the inherited stencil and work queue but requires matching neighbour inputs and protects them against reuse. The results make a conditional case for that complete configuration; they do not support replacing the barrier in every workload.

## Introduction

A shorter elapsed time is an incomplete reason to change how a diffusion solver advances. The inherited baseline, B, uses a global barrier after each step and meets the stated final-error requirement. Removing that barrier and consuming the latest buffer contents, as configuration U does, is faster in every supplied case but fails the requirement throughout. A useful replacement must therefore be compared with B on both accuracy and cost, rather than ranked by time alone.

Configuration G supplies such a candidate by allowing interior work to continue while neighbour messages travel. Boundary work still waits for every required edge value to match its partition epoch and numerical step. Keeping two incoming slots per interface adds storage; retaining a slot until release adds a constraint on producer progress. These decisions belong in the comparison because they make the proposed overlap usable. The question is where that complete change offers a gain, not whether its fastest record exceeds the unchecked mode.

## Main result

Within each case, the modes share the initial field, grid, partition plan, floating-point precision and 2,000 steps. Relative final-field error against serial execution must not exceed 1e-6. B and G qualify in all six cases. Under skew, G changes small-grid time from 244 to 203 ms and large-grid time from 955 to 730 ms. In contrast, the balanced small grid rises from 120 to 127 ms and the balanced large grid changes from 480 to 469 ms. The contrast makes workload choice part of the result, although these samples do not identify a hardware bottleneck.

Migration and traffic-burst times fall from 710 to 604 ms and from 868 to 752 ms. The burst error, 9.3e-7, is closest to the criterion. Added memory is 9, 38 and 24 MiB for the small, large and remaining grids respectively. Thus the measured quantity represented by the DEMO is time for an accuracy-qualified configuration at higher storage cost, not a free speedup.

## Why the overlap needs both decisions

Suppose W0 needs step 17, W1 has sent it and is preparing step 18, and step 16 arrives late. A ready flag cannot tell W0 which value it needs; epoch-and-step matching does. A correct label cannot keep step 17 available if the producer may overwrite its slot; release acknowledgement controls reuse. A free second slot permits another value, while two live slots force the producer to wait. Boundary updates require all applicable edge neighbours; ghost values are copied inputs, with no diagonal exchange.

On a missing-input timeout, every worker returns to the last completed barrier snapshot and reruns using B. Separate old-epoch, full-slot and fallback traces exercise these branches (12/12, 12/12 and 4/4), without reliability estimates or restart timings. The timing table excludes these timeout episodes. No repeats, component ablations, physical execution or prior-art search establish broader performance or novelty. The complete design remains the unit of the supported comparison.
