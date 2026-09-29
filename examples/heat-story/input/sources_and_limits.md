# Source and scope record

DEMO FICTION applies to every file in this input directory. The study, case names, design history, workload outcomes, and numeric results were created solely as editing material. No real publication, prior author, research group, device, simulator, laboratory, or customer is represented.

The mathematical model is explicitly defined in manuscript.md and implementation_notes.md. The two-cell arithmetic and exponential inequalities can be checked directly from those definitions. They require no external citation. Conservation is an algebraic statement about opposite uses of the same face flux; the small energy residuals in the CSV files are nevertheless stipulated floating-point outcomes, not observations.

results_runtime.csv contains 18 rows: six invented cases and three methods per case. results_guard_sweep.csv contains six rows for one case at different eta values. The 0.003 row in the sweep duplicates the moving_source G setting in the runtime table and is not an additional observation. All rows explicitly identify their provenance as DEMO_STIPULATED.

The time components are a fictional cost-accounting model. Face-evaluation fractions, final-temperature errors, and energy-balance residuals are invented values consistent with the stated comparisons. In particular, the temperature-error values were not derived by integrating the PDE and should not be presented as reproduced simulation output. No source arrays or temperature trajectories are supplied. Arithmetic reproducibility must be distinguished from solver reproducibility.

The status field ACCEPTED means that the stipulated stepping path completes without a numerical-input or stability exit. It does not override accuracy_pass. A row can therefore complete all accepted time steps while failing the separate temperature-error acceptance rule.

Within a case, all three methods have the same cell count, accepted-step count, prescribed time grid, modeled source sequence, coefficient law, capacity, and endpoint. V is the full-refresh numerical comparison, not an analytical physical ground truth. max_abs_error_K denotes the maximum over cells of the absolute difference from V at the final time only. There is no time-history norm. The acceptance rule is max_abs_error_K ≤ 0.010 K. Error values equal to that limit would pass.

energy_balance_rel is abs(sum_i C_i × (T_i,final − T_i,initial) − E_source) / max(abs(E_source), 1 J). It assesses the stipulated net energy accounting and does not assess the spatial accuracy of temperatures. All modeled source totals are nonnegative. The unprovided individual source totals prevent independently recomputing these residuals.

face_eval_pct measures evaluated faces, including startup, divided by the work of refreshing all interior faces on all 1,000 accepted steps. Consequently, V and every other method need only 0.1 percent for beta-zero conductance: one initial evaluation divided by 1,000 steps. P4 needs exactly 25 percent in a nonconstant case. G's percentages include its initial full refresh. Group-test costs are zero for V, P4, and the beta-zero bypass.

memory_MiB reports the modeled reserved arrays only, with 1 MiB = 1,048,576 bytes. It excludes program text, stack, allocator overhead, runtime libraries, and operating-system memory. The 64- and 96-byte-per-cell allocation definitions are in implementation_notes.md.

The named comparison mechanisms are ordinary design descriptions, not a sourced related-work survey. Claims of first use, actual novelty, superiority to published methods, experimental speedup, significance, or production readiness are unsupported by this package. No references were invented to fill that gap.
