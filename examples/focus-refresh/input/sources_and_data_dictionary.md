# DEMO source and data inventory

## Internal source register

| ID | Source | What it establishes | What it does not establish |
|---|---|---|---|
| S-GEO | `apparatus_and_operations.md` | Declared geometry, idealized sensor and motion rules | A built apparatus, certified collision protection |
| S-IMPL | `construct_demo.py` | Executable policy behavior and exact deterministic construction | Real autofocus behavior, literature novelty |
| S-INPUT | `data_v1/events.csv` | Complete fixed list of 24 invented exchanges | A population distribution or random sampling |
| S-FIELD | `data_v1/field_results.csv` | All nine center errors for every policy/event pair | Image quality away from centers |
| S-RUN | `data_v1/run_results.csv` | Declared time budget and acceptance for all 96 pairs | Instrument elapsed time or recovery-adjusted throughput |
| S-TRACE | `data_v1/probe_trace.csv` | Exact local waypoints, measured values, and raised transfers | Common registration sensor paths |
| S-DRAFT | `rough_manuscript_v0.md` | Unreconciled author's working prose | Independent evidence for its assertions |

No external articles, experiments, sources, organizations, customers, or real measurement files were consulted or invented. All candidate names are local labels. This provenance statement applies even when a generated number has many decimal places.

## CSV grains and keys

* `events.csv`: one row per `event_id`; 24 rows. `event_ordinal` fixes the formulas. `condition` has eight rows each of `broad_row_change`, `east_local_change`, and `combined_change`.
* `run_results.csv`: one row per (`event_id`,`policy`); 96 rows. There are exactly PLANE, ALL9, ROW3, and SHIFT3 for every event.
* `field_results.csv`: one row per (`event_id`,`policy`,`site_id`); 864 rows. Every run has nine rows, whether or not it accepts.
* `probe_trace.csv`: one row per (`event_id`,`policy`,`operation_index`) for executed local actions. An action is a `probe` or a final `return`. Returns have empty measurement values. PLANE intentionally contributes no local action rows.

## Principal columns

Spatial coordinates and distances are in mm; angles are in degrees; surface values and focus errors are in micrometers (um); times are in seconds. `plane_ax_um_per_mm` and `plane_by_um_per_mm` are plane slopes. `plane_c_um` is its intercept. `xy_tx_mm`, `xy_ty_mm`, and `xy_rotation_deg` are fully removed by the exact common registration.

`stored_local_um` is the old residual after its original plane was removed. `true_change_um` is current local change relative to that residual. `current_plane_um` is the newly fitted global plane evaluated at the site. `measured_local_um` includes bounded synthetic probe error. `commanded_local_um` is what a policy uses, whether observed, copied, or retained. `true_surface_um` and `commanded_surface_um` add the common plane back. `focus_error_um` is true minus commanded; `abs_focus_error_um` is its magnitude.

`accepted_center` is 1 iff absolute error <=8 um. `accepted_centers` is its nine-site sum. `accepted_event` is 1 iff that sum is 9. `was_probed` refers to an actual local measurement, not to a borrowed SHIFT3 correction or common registration. `row_triggered` is only meaningful for ROW3. `triggered_rows` is an ordered concatenation of its row letters, empty when none triggers.

`local_probe_count` excludes datum-plane measurements and common acquisition stops. `local_probe_sequence` shows each local center exactly once in execution order. `local_path_mm` includes the departure from and return to PARK. `local_retract_count` counts segments whose low-travel head envelope intersects the clip. The timing component columns sum to `local_calibration_s`. `total_cycle_s` adds the common 5.0 s registration and 8.59 s acquisition. These are modeled budgets for every attempt, including unsuccessful attempts.

`dataset_metadata.json` documents constants, scope, array sizes, and the common acquisition route. `generated_files_sha256.json` fixes the initial generated data files. The generator's maximum exported rounding is eight decimal places; checks should allow about 1e-6 for accumulated floating-point differences.

## Two complete tabular views

`table_view_1_condition_results.csv` contains all 12 condition/policy groups. `constructed_events` is 8 for each group; `accepted_events` counts nine-center successes; `accepted_centers` has denominator `total_centers`=72; `worst_abs_focus_error_um` is the maximum over all group centers; `mean_total_cycle_s` averages all eight attempts, including failures.

`table_view_2_all_attempt_costs.csv` contains all four policies over all 24 events. It reports accepted-event counts, arithmetic mean probe count, mean local route distance, mean local raised-transfer count, mean local calibration time, and the minimum/mean/maximum complete cycle time. These descriptive cost columns include unsuccessful attempts. The policy rows are paired evaluations on the same fixed event set. These source views can be checked directly against `run_results.csv`; they do not prescribe the final manuscript's table layout.

## Reporting restrictions attached to these records

Count denominators explicitly. A policy/event pair is paired with the other policies on the same constructed event. A field is nested inside its event. The packet supplies neither physical repeats nor independently sampled carriers. Means across the fixed grid are descriptive summaries only. Do not infer statistical confidence or significance from the 864 field rows. Failed events and slower cases belong in the report. Derived percentages must specify whether they compare local calibration or complete cycle time and which events are included.
