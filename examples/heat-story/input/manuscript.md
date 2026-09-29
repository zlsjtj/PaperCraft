# Notes from a heat-transport solver revision

DEMO FICTION: This entire manuscript describes an invented engineering study. All timings, errors, workloads, and implementation outcomes are stipulated demonstration material. No program was benchmarked, no physical experiment occurred, and no claim of actual novelty is made.

## Abstract

This draft records changes to a two-dimensional finite-volume heat program that evaluates temperature-dependent face conductances. We first arranged coefficient evaluation into contiguous loops and then considered keeping some coefficients between time steps. A group test uses temperature changes since the last coefficient update. Passing groups retain their stored coefficients; other groups evaluate them again. A face has one owner, and its stored heat flow enters its two neighboring cells with opposite signs. The demonstration accounting covers six invented cases and a separate tolerance sweep. Some cases reduce the modeled execution time, whereas rapid changes and a small domain increase it. A fixed four-step update schedule is also included and is usually faster, but its stipulated temperature errors frequently exceed the chosen acceptance limit. These results are material for developing the design, rather than evidence from an executed solver.

## Program and initial changes

The motivating application in this fictional study is repeated thermal analysis of a thin plate with spatially varying heat input. The mesh is rectangular, all cells have positive heat capacity, and the face law is deliberately simple. Insulated external faces carry no heat. Prescribed power enters as a cell source, so changing the heater pattern does not change the mesh connectivity. The moving-source case shifts the heating region during the interval. The switching-load case alternates prescribed source patterns much more abruptly.

Our first version rebuilt every interior face conductance at each explicit time step. Coefficient calculation and flux calculation were originally interleaved. Separating them permits contiguous coefficient evaluation and supplies the reference implementation V in the tables. V uses vector-friendly loops and one flux value per face. It is therefore already a fairly favorable comparison for a coefficient reuse scheme. For constant conductance, it computes the coefficients once outside the stepping loop. We retain this special case when comparing methods.

Keeping coefficients for several steps is an existing general numerical implementation choice. We use a simple version, P4, which rebuilds every coefficient on steps numbered zero, four, eight, and so forth. Its schedule is independent of the evolving temperature. P4 uses the same flux and temperature-update code as V. It helped establish how much coefficient work could be removed before adding decisions and storage. No literature search was performed for this fictional draft, so this description does not establish priority for any mechanism.

## Equations used in the code sketch

For an interior face f joining cells i and j, the conductance depends on the mean of the two temperatures. G0 is positive and beta is a fixed nonnegative sensitivity in each case. Temperature differences are in kelvin even when temperatures are written in degrees Celsius.

Equation: G_f(T) = G0 × exp[beta × ((T_i + T_j)/2 − T_ref)]

Equation: q_f = G_f × (T_i − T_j)

Equation: C_i × (T_i,next − T_i)/dt = P_i − Σ_f s_if × q_f

Here C_i is heat capacity, P_i is prescribed power, and s_if is positive for a face directed out of cell i and negative for a face directed into it. All fluxes use the old temperature array. A separate pass writes the next array. Opposite signs make the internal heat exchange cancel when the cell balances are summed. This statement remains true for stored, approximate conductances; it does not make those conductances equal to the current constitutive law.

For nonnegative conductances, the temperature-only part of the explicit update is a convex combination when its row sum is at most one. The sketch uses a stricter operational threshold of 0.95. Source terms are excluded from that convex-combination statement and can independently increase or decrease a temperature.

Equation: sigma_i = dt × Σ_f G_used,f / C_i

## Later group implementation

The next change divides the mesh into 16 by 16 cell groups. A deterministic owner stores each interior face once, including faces crossing group boundaries. Each owner also holds snapshots of both endpoint temperatures needed by its faces. Thus a group test includes temperatures on the other side of a group boundary. The snapshots share the last refresh time of that owner's coefficients; another group's refresh does not change them.

Let D be the largest absolute difference between a needed endpoint temperature and its stored snapshot. The largest change of any face-mean temperature is no greater than D. The exponential law then gives the following test, with eta denoting a user-selected local coefficient tolerance.

Equation: bound = exp(beta × D) − 1

Equation: abs(G_current − G_cached) / G_cached ≤ bound

If bound is at most eta, the group reuses its coefficients. Otherwise, it refreshes every owned face and its snapshots. The method is called G in the tables. Its test is conservative for a group containing a small hot region because every owned face is refreshed when that region triggers the test. We did not add smaller subgroups to this draft implementation. Their extra metadata and branch work would need separate accounting.

The test is performed before forming any flux. All groups finish their decisions before the row sums and fluxes are evaluated. Changing a face coefficient halfway through the accumulation would make the energy accounting harder to interpret and is excluded here. Groups with beta equal to zero bypass the snapshot path and use V's constant-coefficient handling.

## Small checks during development

Consider two isolated cells with temperatures 40 and 20 degrees Celsius, each with heat capacity 100 J/K. Take G0 equal to 2 W/K, beta equal to 0.01 per kelvin, T_ref equal to 20 degrees Celsius, and dt equal to one second. The face conductance is 2.21034184 W/K and the heat flow is 44.20683672 W. The next temperatures are 39.55793163 and 20.44206837 degrees Celsius. Their capacity-weighted sum is unchanged within the displayed rounding. Each row sum is approximately 0.0221034, below the operational threshold.

For a subsequent group snapshot test with D equal to 0.2 K, the relative coefficient bound is approximately 0.00200200. It passes eta equal to 0.003. At D equal to 0.4 K, the bound is approximately 0.00400801, so the same group refreshes. These examples check the arithmetic and control decisions. They do not supply a temperature-error guarantee over many steps.

## Demonstration accounting

The first CSV separates group-test time, coefficient time, and all remaining transport work. Total time is their sum. It includes 1,000 accepted steps per case; rejected trials do not occur in these six case descriptions. Each method uses the same prescribed step sizes, source sequence, mesh, and final simulated time within a case. The performance denominator is V's total time for that case. P4 and G errors are stipulated maximum absolute final-temperature differences from V, whose own discretization error is not evaluated.

For the slow plate, V takes 400 ms in this invented accounting and G takes 354.6 ms. G evaluates 10 percent of the full-refresh face work. Nevertheless, the total saving is only 45.4 ms because the test and transport passes remain. P4 takes 329 ms and satisfies the 0.010 K temperature-error limit in this case. It is a useful alternative here. The ramp and moving-source cases give smaller G improvements, and the stipulated P4 errors exceed that limit.

The switching load has 96 percent face evaluation under G and a total of 1723.2 ms, compared with 1600 ms for V. The small mesh also loses time: 10.32 ms compared with 8 ms. Constant conductance produces identical totals for V and G because both leave the group mechanism inactive. The allocated array memory increases from 64 to 96 bytes per cell when G is active, a 50 percent increase. This allocation includes a deliberately padded snapshot and metadata reserve.

## Tolerance choices and incomplete checks

The second CSV varies eta only for the moving-source case. At 0.0005, the additional group work outweighs the saved coefficient work. At 0.003, the stipulated error is 0.009 K and satisfies the selected limit. At 0.010, the total time falls further, but the stipulated error is 0.038 K and fails that limit. A smaller coefficient bound can therefore be useful without the timing benefit being monotonic in practical value. The local bound alone cannot select an acceptable temperature error.

The implementation notes also record three invented exception traces. A finite but large row sum rejects a proposed step and halves its size before a full refresh. A nonfinite source aborts that proposed step without committing the next-temperature array. An exponential overflow has the same abort behavior. These exits matter because a stale coefficient should not silently convert a rejected constitutive evaluation into a successful time step. No rejected step contributes to the accepted-step count.

## Discussion and conclusion

The draft leaves several limitations unresolved. The error numbers have no stored trajectories behind them, and the times are an accounting construction rather than processor measurements. The group test itself includes an exponential evaluation, although only once per active group, and snapshot traffic can dominate when coefficient evaluation is cheap. There is no measured cache analysis, parallel scaling, or mixed-material extension. The common energy-balance residual checks paired accumulation but cannot demonstrate an accurate thermal solution. Within these explicit limits, the design notes describe a complete decision path and show where its modeled cost can be recovered and where it cannot.
