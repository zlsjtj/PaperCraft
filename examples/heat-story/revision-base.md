# DEMO: Conductance Reuse with Consistent Snapshots in Explicit Heat Transport

DEMO FICTION. This paper describes an invented engineering study. All workloads, timings, errors, residuals, and implementation outcomes are stipulated editing material. There is no executable solver, measured performance, physical experiment, or claim of actual novelty.

## Abstract

Reusing temperature-dependent conductances can avoid repeated work, but a fixed refresh schedule ignores how rapidly temperatures change. We describe a groupwise decision that compares current endpoint temperatures with the snapshots used to form each stored coefficient. Keeping these snapshots with the coefficient's owner makes the comparison valid even across group boundaries. The design combines this local change bound with separate rules for accepting or discarding a time step. Fictional accounting then asks whether avoided coefficient work repays the decision and storage costs. The method reduces total time in three of five nonconstant cases but loses time on switching loads and a small mesh. All five stipulated final-temperature differences meet a 0.010 K comparison limit, with 50% greater reserved array memory. A fixed four-step schedule is faster but fails that limit in four cases. Reuse is therefore conditional: its guard can cost more than it saves, and its local bound does not guarantee global temperature accuracy.

## 1. The decision between refreshing and reusing

A thin plate under slowly changing heating need not rebuild every temperature-dependent face conductance at every step. A moving or switching heater makes that shortcut harder: the same number of elapsed steps can conceal very different temperature changes. The useful question is therefore when a stored coefficient can still be reused, and whether deciding this costs less than recomputing it.

The proposed method G answers the first question with temperature snapshots taken when its coefficients were formed. A boundary face makes the technical difficulty concrete: the coefficient depends on temperatures in two groups, whose refreshes need not occur together. Both endpoint snapshots must remain attached to that coefficient's refresh event. Otherwise, the test can refer to a different state from the coefficient it is meant to check. Figure 1 makes this relationship explicit; Section 3 derives the bound and explains the accepted-state rules.

Reuse itself is an existing implementation choice. The full-refresh reference V separates the originally interleaved coefficient and flux calculations into contiguous, vector-friendly loops. It already computes one flux per face and evaluates constant conductances once. P4 uses V's flux and temperature-update code, refreshing coefficients every four accepted steps. These inherited choices are not contributions of G. The comparison in Figure 2 asks what G's conditional decision adds: acceptable final-temperature differences at what total-time and memory cost. Its mixed outcomes delimit the design's use rather than establish universal advantage. No literature search supports a priority claim.

## 2. Model and the quantities that reuse must preserve

The two-dimensional finite-volume mesh is rectangular; all demonstration domains are square. External faces are insulated. Prescribed cell power changes the heating pattern without changing connectivity. For an interior face f between cells i and j, G0 is a fixed positive scalar, beta is fixed and nonnegative, and T_ref is a fixed reference temperature. Temperature differences are in kelvin even when temperatures are expressed in degrees Celsius.

Equation: G_f(T) = G0 × exp[beta × ((T_i + T_j)/2 − T_ref)]

Equation: q_f = G_f × (T_i − T_j)

Equation: C_i × (T_i,next − T_i)/dt = P_i − Σ_f s_if × q_f

Here C_i is strictly positive heat capacity and P_i is prescribed power. The sign s_if is positive for a face directed out of cell i and negative for a face directed into it. Every flux uses the immutable old-temperature array. One oriented flux is stored per face and enters the two adjacent balances with opposite signs; a separate pass writes the next-temperature array. Summing cell balances therefore cancels internal exchange even with approximate cached conductances. Cancellation does not establish that the conductances match the current law or that temperatures are accurate.

The diffusive update is a convex combination for nonnegative conductances when its row sum is at most one. The design uses the stricter operational threshold 0.95, calculated from the coefficients actually selected for the trial:

Equation: sigma_i = dt × Σ_f G_used,f / C_i

This condition excludes source terms. It neither limits prescribed cooling nor proves positivity under arbitrary sources, and it is not a global temperature-error estimator.

## 3. Making the reuse bound refer to the right state

### 3.1. Ownership and endpoint snapshots

The mesh is partitioned into 16 × 16 cell groups. Each face is oriented from the smaller to the larger row-major cell index; the group containing the first endpoint owns it. That owner stores the coefficient and snapshots of every endpoint needed by its faces, including endpoints in neighboring groups. All snapshots are versioned by the owner's refresh counter.

Figure 1. A boundary face retains its owner's refresh history. The cells are a detail of different 16 × 16 groups; i < j assigns face f to A. Dashed lines link endpoints to their stored temperatures at A's refresh r. If A reuses while B refreshes at its own counter s, A's coefficient and both snapshots stay at r. The counters r and s are independent.

A face crossing a group boundary explains why ownership matters. Its coefficient was evaluated using both endpoint temperatures at the owner's refresh. Updating the neighboring group's coefficients must not overwrite either associated snapshot: doing so would compare a stored coefficient against temperatures from a different event. The nonowner therefore leaves those snapshots untouched. The later guard therefore measures temperature change since that coefficient was formed.

Let D be the largest absolute change from an owner's snapshots among all endpoints its faces require. The change of each face-mean temperature is at most D. For the stated fixed, nonnegative beta and positive cached conductance, the exponential law yields:

Equation: bound = exp(beta × D) − 1

Equation: abs(G_current − G_cached) / G_cached ≤ bound

G reuses the group's coefficients when bound is at most the user-selected local tolerance eta, including equality. Otherwise, it refreshes every owned face and the corresponding snapshots. A small hot region can thus trigger refresh of an entire group. Smaller subgroups are not included; their metadata and branching costs remain unaccounted for. Each active group test itself evaluates an exponential and reads snapshots. When beta is zero, all methods use one initial coefficient evaluation, and G bypasses both snapshot processing and its extra allocation.

### 3.2. Completing or discarding a proposed step

Every trial first validates old temperatures, capacities, dt, and current source values: all must be finite, with positive capacities and dt. Invalid inputs abort rather than entering a retry loop. Initialization, restart, and retry require a global refresh; otherwise the selected method makes its refresh decisions. Nonfinite intermediate values are rejected. All decisions finish before any row sums or fluxes are formed, so a coefficient cannot change during accumulation.

Every selected coefficient must be finite and strictly positive. Exponential overflow or underflow to zero exits with INVALID_COEFFICIENT; halving dt cannot repair a constitutive evaluation at unchanged old temperatures. If the maximum sigma exceeds 0.95, the trial is discarded, dt is halved, and all coefficients are refreshed on retry. Eight halvings are permitted; continued failure exits with RETRY_LIMIT and preserves the last accepted state.

The face pass then writes each flux once, and the cell pass constructs the next temperatures. Nonfinite outputs cause INVALID_OUTPUT and retain the old array. Acceptance commits the array swap, simulated time, and accepted-step count together. Only accepted steps accumulate source energy as dt × sum(P_i). Discarded trials add neither energy nor time. Temporary refreshed caches are invalidated on abort; restart always refreshes globally. A parallel implementation would also require a completed face-pass barrier before the cell pass, but none has been constructed.

### 3.3. Arithmetic and exception examples

For two isolated cells at 40 and 20 °C, with capacities 100 J/K, G0 = 2 W/K, beta = 0.01 K⁻¹, T_ref = 20 °C, and dt = 1 s, the conductance is 2.21034184 W/K and flux is 44.20683672 W. The next temperatures are 39.55793163 and 20.44206837 °C. Their capacity-weighted sum is unchanged within displayed rounding; each sigma is approximately 0.0221034. At D = 0.2 K, the bound is approximately 0.00200200 and passes eta = 0.003; at D = 0.4 K, approximately 0.00400801 triggers refresh. These arithmetic examples do not guarantee accuracy over multiple steps.

Three constructed exception traces specify different exits. R1 starts with a full-refresh sigma of 1.10 at dt = 1 s, discards that trial, and accepts dt = 0.5 s with sigma = 0.55 because old temperatures are unchanged. It ends at 0.5 s, not at the original one-second endpoint. R2 supplies a NaN source and exits INVALID_INPUT before coefficient decisions. R3 supplies an exponent of 800 in binary64 arithmetic and exits INVALID_COEFFICIENT on overflow. R2 and R3 commit no steps. All three are excluded from the accounting tables and are control descriptions, not execution logs.

## 4. What the fictional comparisons measure

Figure 2 summarizes the comparison; Table 1 retains all accounting records for V, P4, and G on matched meshes, source sequences, constitutive parameters, prescribed time grids, and endpoints. The square meshes are 64 × 64, 512 × 512, or 1024 × 1024 cells. Every case stipulates 1,000 accepted steps at dt = 0.1 s, ending at 100 s, with maximum sigma below 0.95 and zero rejected trials. Sources may change with accepted-step number. Nonconstant cases use G0 = 2 W/K, beta = 0.01 K⁻¹, T_ref = 20 °C, uniform capacity 100 J/K, and initial temperature 20 °C; static conduction sets beta to zero.

The slow plate has a broad, gradually changing stationary source. The boundary ramp heats cells along one edge while external faces remain insulated. The moving source translates a compact heated region; switching load alternates two source regions. The small mesh has an alternating source, and static conduction has a stationary source. Exact source arrays are absent, so these are scenario descriptions, not executable workloads.

Total time is guard plus coefficient plus transport time. Transport includes validation, sigma checks, flux construction, temperature update, and bookkeeping. Startup is included; I/O, checkpoint serialization, visualization, and mesh construction are excluded. Nonconstant coefficient time scales linearly with the stipulated fraction of V's full-refresh face evaluations, ignoring vector occupancy and cache effects. Face fractions include startup and divide by refreshing every interior face over all 1,000 steps. Thus P4 uses 25%, while every beta-zero method uses 0.1%.

Errors are maximum absolute final-temperature differences over cells from V, whose discretization error is unknown. There is no time-history norm. Accuracy passes at error ≤ 0.010 K, including equality. ACCEPTED only means the stipulated stepping path completes; it does not imply accuracy. The relative energy residual is abs(sum_i C_i × (T_i,final − T_i,initial) − E_source) divided by max(abs(E_source), 1 J). Source totals are nonnegative but unprovided, preventing independent residual recomputation. This residual concerns net energy, not spatial temperature accuracy.

The common allocation is 64 bytes per cell: two temperature arrays use 16 bytes, capacity and source arrays 8 each, and padded face-coefficient and face-flux storage 16 each. Two faces per cell are reserved even at boundaries. Active G adds 32 bytes per cell for snapshots, indices, counters, and aligned metadata: 96 bytes total, a 50% increase. The reserve includes padding; not every byte holds snapshot data. Group dimensions divide every mesh dimension. P4 and the beta-zero bypass retain the common allocation. One MiB is 1,048,576 bytes; program text, stack, allocator, libraries, and operating-system memory are excluded.

## 5. Savings depend on overhead and acceptable error

Figure 2 brings time and final error together: a faster method is useful here only if it also meets the stated error limit. This is a comparison of stipulated outcomes, not measured execution or a validated solver trajectory.

Figure 2. Read modeled savings with final-temperature error. G uses eta = 0.003 and reserves 50% more array memory when active; the constant-law bypass adds none. (a) Total-time change from V is (t_method/t_V − 1) × 100%; negative values are faster. Crossed diamonds fail the 0.010 K limit. V defines zero change and zero comparison error in each case. (b) Complete slow-plate costs: G removes 90% of face evaluation but only 11.35% of total time. Values are stipulated, without sampled uncertainty; the full accounting records remain in Table 1.

For the slow plate, G reduces total time from 400 to 354.6 ms, an 11.35% reduction using V as denominator. Removing 90% of face evaluation saves 86.4 ms of coefficient work, but a 35 ms guard and 6 ms more transport leave only 45.4 ms net savings. P4 is faster and uses less memory while also meeting the error limit: 329 ms and 0.006 K error.

The boundary ramp and moving source reduce G totals from 420 to 390 ms and from 1580 to 1510 ms, with errors of 0.007 and 0.009 K. P4 is faster at 345 and 1285 ms, but its respective errors of 0.024 and 0.071 K fail the limit. G therefore offers an acceptable stipulated alternative in these cases at smaller savings and greater memory cost.

Switching load reverses the timing result: G evaluates 96% of faces and takes 1723.2 ms versus V's 1600 ms. The small mesh also loses, at 10.32 versus 8 ms with 91% face evaluation. G passes the error rule in both; P4 takes 1300 and 6.5 ms but fails at 0.114 and 0.018 K. Constant conductance gives identical 300 ms totals and memory for all methods. These negative and bypass cases rule out a universal timing advantage in the accounting model.

*Table 1. Complete runtime accounting records. Every row has provenance DEMO_STIPULATED, accepted_steps = 1,000, dt_s = 0.1, final_time_s = 100, accuracy_limit_K = 0.010, rejected_trials = 0, and status = ACCEPTED. Eta is 0.003 for G and NA for V/P4. Faces denotes face_eval_pct; energy residual denotes energy_balance_rel. Times are milliseconds; memory is reserved arrays in MiB.*

| Case | Cells | Method | Faces (%) | Guard | Coefficient | Transport | Total | Error (K) | Accuracy pass | Energy residual | Memory (MiB) |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| plate_slow | 262144 | V | 100 | 0 | 96 | 304 | 400 | 0 | TRUE | 1.7e-14 | 16 |
| plate_slow | 262144 | P4 | 25 | 0 | 24 | 305 | 329 | 0.006 | TRUE | 2.1e-14 | 16 |
| plate_slow | 262144 | G | 10 | 35 | 9.6 | 310 | 354.6 | 0.003 | TRUE | 2.4e-14 | 24 |
| boundary_ramp | 262144 | V | 100 | 0 | 100 | 320 | 420 | 0 | TRUE | 2.0e-14 | 16 |
| boundary_ramp | 262144 | P4 | 25 | 0 | 25 | 320 | 345 | 0.024 | FALSE | 2.6e-14 | 16 |
| boundary_ramp | 262144 | G | 36 | 36 | 36 | 318 | 390 | 0.007 | TRUE | 2.8e-14 | 24 |
| moving_source | 1048576 | V | 100 | 0 | 400 | 1180 | 1580 | 0 | TRUE | 3.0e-14 | 64 |
| moving_source | 1048576 | P4 | 25 | 0 | 100 | 1185 | 1285 | 0.071 | FALSE | 3.7e-14 | 64 |
| moving_source | 1048576 | G | 51 | 120 | 204 | 1186 | 1510 | 0.009 | TRUE | 4.1e-14 | 96 |
| switching_load | 1048576 | V | 100 | 0 | 420 | 1180 | 1600 | 0 | TRUE | 3.2e-14 | 64 |
| switching_load | 1048576 | P4 | 25 | 0 | 105 | 1195 | 1300 | 0.114 | FALSE | 4.5e-14 | 64 |
| switching_load | 1048576 | G | 96 | 130 | 403.2 | 1190 | 1723.2 | 0.009 | TRUE | 4.8e-14 | 96 |
| small_mesh | 4096 | V | 100 | 0 | 2 | 6 | 8 | 0 | TRUE | 8.0e-15 | 0.25 |
| small_mesh | 4096 | P4 | 25 | 0 | 0.5 | 6 | 6.5 | 0.018 | FALSE | 8.8e-15 | 0.25 |
| small_mesh | 4096 | G | 91 | 2.3 | 1.82 | 6.2 | 10.32 | 0.002 | TRUE | 9.0e-15 | 0.375 |
| static_conduction | 262144 | V | 0.1 | 0 | 0.1 | 299.9 | 300 | 0 | TRUE | 1.5e-14 | 16 |
| static_conduction | 262144 | P4 | 0.1 | 0 | 0.1 | 299.9 | 300 | 0 | TRUE | 1.5e-14 | 16 |
| static_conduction | 262144 | G | 0.1 | 0 | 0.1 | 299.9 | 300 | 0 | TRUE | 1.5e-14 | 16 |

Table 2 varies only eta for the moving source. The 0.003 row repeats Table 1's setting and is not an independent observation.

*Table 2. Complete tolerance-sweep records. All rows have provenance DEMO_STIPULATED, case moving_source, method G, cells = 1,048,576, accepted_steps = 1,000, dt_s = 0.1, final_time_s = 100, accuracy_limit_K = 0.010, memory_MiB = 96, rejected_trials = 0, and status = ACCEPTED. Times are milliseconds; faces and energy residual use Table 1's definitions.*

| Eta | Faces (%) | Guard | Coefficient | Transport | Total | Error (K) | Accuracy pass | Energy residual |
|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 0.0005 | 88 | 120 | 352 | 1186 | 1658 | 0.001 | TRUE | 3.3e-14 |
| 0.001 | 72 | 120 | 288 | 1186 | 1594 | 0.003 | TRUE | 3.6e-14 |
| 0.002 | 61 | 120 | 244 | 1186 | 1550 | 0.006 | TRUE | 3.8e-14 |
| 0.003 | 51 | 120 | 204 | 1186 | 1510 | 0.009 | TRUE | 4.1e-14 |
| 0.006 | 32 | 120 | 128 | 1186 | 1434 | 0.019 | FALSE | 4.3e-14 |
| 0.01 | 18 | 120 | 72 | 1186 | 1378 | 0.038 | FALSE | 4.7e-14 |

At eta = 0.0005 and 0.001, totals of 1658 and 1594 ms exceed V's 1580 ms despite passing accuracy. Values 0.002 and 0.003 both save time and pass. Values 0.006 and 0.010 reduce time further but fail at 0.019 and 0.038 K. Thus a local coefficient tolerance cannot by itself select acceptable solution error. There is no automatic eta controller. Small energy residuals across passing and failing rows also show why energy accounting cannot replace the temperature comparison.

## 6. Research gaps

The bound and two-cell arithmetic are directly checkable from the defined model. The times, face fractions, errors, and floating-point residuals are stipulated, not derived from a solver trajectory. They have no sampled variance. Missing source arrays and trajectories prevent solver reproduction; arithmetic reproducibility is a narrower property. Snapshot traffic, measured cache behavior, vector occupancy, and parallel scaling remain untested, as do mixed materials and time-dependent beta. Without literature validation, this paper establishes neither novelty nor superiority to published methods, statistical significance, or production readiness.

## 7. Conclusion

The design makes reuse depend on temperature change since the coefficient's own refresh, rather than elapsed steps alone. Consistent endpoint snapshots make that comparison interpretable, while paired fluxes and explicit abort rules preserve distinct accounting obligations. The fictional comparisons favor G only where saved coefficient work exceeds guard and transport costs while the separate final-error rule passes. They motivate that conditional design judgment without converting a local bound into a global accuracy guarantee or constructed accounting into experimental speedup.