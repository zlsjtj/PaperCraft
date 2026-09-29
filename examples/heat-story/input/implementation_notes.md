# Implementation notebook

DEMO FICTION. This document is a design record for an invented solver. There is no executable solver, real machine timing, real application trace, literature validation, or experimental evidence in this package.

## Arrays and ownership

The domain is a square two-dimensional cell mesh with insulated external faces. The synthetic cases use 64 × 64, 512 × 512, or 1024 × 1024 cells. The coefficient law and explicit update are given in the manuscript. G0, beta, and the reference temperature are constant scalar parameters within a case. Cell capacity is strictly positive; prescribed cell power may change with accepted step number. Material mixtures and time-dependent beta are outside this design.

A face is oriented from the endpoint with smaller row-major index to the endpoint with larger index. The 16 × 16 group containing that first endpoint owns the face. The owner stores the cached coefficient and the snapshot temperatures of every endpoint required by its owned faces, including any endpoint in another group. Each group's snapshots are versioned by that group's refresh counter. A nonowner must not overwrite those snapshots when it refreshes its own coefficients. This avoids comparing a coefficient with temperatures from a different refresh event.

All state reads used by a proposed step come from one immutable old-temperature array. A separate next-temperature array becomes current only after the trial is accepted. The face-flux pass writes one oriented flux per face. The cell pass reads those fluxes with the appropriate signs. Parallel execution would require a completed face-pass barrier before the cell pass; no parallel implementation has been constructed.

The common allocation model reserves 64 bytes per cell: two temperature arrays totaling 16 bytes, one capacity array of 8 bytes, one source array of 8 bytes, padded face-coefficient storage of 16 bytes, and padded face-flux storage of 16 bytes. A face capacity of two faces per cell is reserved even at boundaries. Active G adds a fixed 32-byte-per-cell reserve for snapshots, indices, counters, and aligned group metadata. This is reserved capacity, not a claim that every byte is useful snapshot data. Group dimensions divide all listed mesh dimensions. Constant beta equal to zero bypasses the added allocation. P4 uses the common allocation.

## Proposed-step sequence

1. Validate all old temperatures, capacities, dt, and current source values. Require finite values, strictly positive capacities, and strictly positive dt. Rejecting invalid inputs aborts the step; it does not start the retry loop.
2. On initialization, after restart, or on a retry, rebuild all coefficients. Otherwise, for G, form each owner's D from its own snapshots and both face endpoints. Reject nonfinite intermediate values. Refresh that owner's entire face set when exp(beta × D) − 1 is greater than eta. Equality reuses the cached coefficients. P4 refreshes on accepted-step numbers divisible by four. V refreshes every accepted step. All three methods use the one-time coefficient evaluation when beta is zero.
3. Verify that every coefficient is finite and strictly positive. Compute sigma for each cell using the actual coefficients selected for this trial. If maximum sigma exceeds 0.95, discard the trial, halve dt, and request a global refresh on retry. Permit eight halvings for one proposed step. If it still fails, exit with RETRY_LIMIT and retain the last accepted state.
4. Form each oriented face flux once and update cell temperatures in the separate output array. Validate that all output values are finite. If not, exit with INVALID_OUTPUT and keep the old array.
5. Commit the array swap, accumulated simulated time, and accepted-step count together. Accumulate supplied source energy as dt × sum(P_i) for that accepted step. Report internal energy change minus this supplied energy. Discarded trials contribute neither energy nor time.

Coefficient overflow or underflow to zero is an invalid constitutive evaluation, with exit INVALID_COEFFICIENT. It does not trigger a dt-halving retry because changing dt cannot repair a coefficient calculated from the same old temperatures. A trial's temporary refreshed caches are invalidated on abort. A restart begins with full coefficient refresh rather than assuming that partially modified cache state matches the restored temperatures.

The row-sum rule constrains only the diffusive part of the explicit update. It is not a limiter for externally prescribed cooling, a proof of positivity under arbitrary sources, or a global temperature-error estimator. The implementation intentionally contains no automatic eta controller.

## Invented exception traces

These traces are constructed control examples and do not represent execution logs.

| Trace | Incoming condition | Expected transition | Committed work |
| --- | --- | --- | --- |
| R1 | A full-refresh trial has maximum sigma = 1.10 at dt = 1 s; old state and source are finite | Discard trial; retry with dt = 0.5 s and global refresh; sigma = 0.55 because the old temperatures are unchanged | One accepted 0.5 s step after one discarded trial |
| R2 | One source value is NaN before any coefficient decision | INVALID_INPUT | Zero accepted steps; old array retained |
| R3 | A refreshed coefficient exponent is 800 in binary64 arithmetic | INVALID_COEFFICIENT on exponential overflow | Zero accepted steps; old array retained |

R1 ends at 0.5 s in this trace. It is not a substitute for a one-second physical-interval benchmark and is excluded from both CSV files. R2 and R3 are excluded as well. Repeating these descriptions cannot produce empirical reliability evidence.

## Accounting notes

The CSV times partition one hypothetical total into group-guard work, face-coefficient work, and transport work. Transport includes validation, sigma checks, flux construction, temperature update, and bookkeeping. Startup is included. No I/O, checkpoint serialization, visualization, or mesh construction cost is included. Rows have no timing variance because they were stipulated, not sampled.

For nonconstant cases, coefficient time scales linearly with the stated percentage of V's full-refresh face evaluations. This assumption deliberately ignores vector occupancy changes and cache effects. Those effects may change actual cost. The group percentage is a stipulated work fraction, not a claim that a particular executable generated the guard decisions.

All nonconstant cases use G0 = 2 W/K, beta = 0.01 K⁻¹, T_ref = 20 °C, uniform capacity 100 J/K, and initial temperature 20 °C. Static conduction sets beta = 0. The source-pattern labels specify only scenario types; exact source arrays have not been supplied. Each main case stipulates 1,000 accepted steps at dt = 0.1 s and final time 100 s, with maximum sigma below 0.95 and no rejected trials. These conditions are assumptions of the accounting rows, not results of a generated trajectory.

plate_slow denotes a broad stationary source changing gradually. boundary_ramp denotes a source applied to cells along one edge of the plate and increasing in time; the external faces themselves remain insulated. moving_source translates a compact heated region. switching_load alternates two source regions. small_mesh uses an alternating source on the 64 × 64 domain. static_conduction uses a stationary source and beta equal to zero. These descriptions are sufficient for the fictional narrative but are not executable workload specifications.
