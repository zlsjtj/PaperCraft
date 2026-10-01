# Original editorial DEMO

All apparatus descriptions, numbers and outcomes below are authored for an editorial exercise, not real measurements or an existing publication. Do not cite them as research evidence. No external sources or literature-priority claims are available.

## Draft fragments

We made a scan controller with reference support, queues, missing-value handling and export. The controller scans numbered sample wells in order. There are a lot of settings and checks. A more complicated mode was added. Results of the modes differ. Some files were not usable. This paper presents the controller and its evaluation.

## Apparatus and implementation notes

An existing laboratory fixture scans the same eight numbered wells with one optical sensor. The sensor returns arbitrary signal units; no concentration, biological property or temperature is inferred. The established scan order, sensor firmware, reference well and reference subtraction are inherited. Reference wells contain a fixed optical standard; sample values in the following fixtures are authored and known to the evaluator.

Three operating modes use the same scan order and electronics. R0 measures the reference once before the eight sample readings and subtracts that value from every sample. R1 measures the reference immediately before each sample and subtracts the paired value; it already handles the stipulated time-varying additive offset. R2 uses a reference measurement immediately before and after each group of two sample readings, then linearly interpolates reference values at the sample acquisition timestamps. Group endpoints are shared by adjacent groups within a scan; the ending reference of one scan is not reused for a later scan. Therefore R0 has 9 acquisitions per scan, R1 has 16, and R2 has 13. No method changes the sample scan order.

The fixture schedule timestamps the start of each acquisition, and all acquisitions have the same prescribed duration. R2 stores both sample readings privately until the ending reference is available; no interim corrected values are exported. If either reference is missing, the group is marked unavailable, not filled using the previous group's reference. A step in offset inside a group is not reconstructed by two endpoints. Interpolation is existing arithmetic, not a new estimator. Queue ownership prevents exporting an incomplete pair but has not been separately timed. The exercise supplies no independent hardware novelty or prior-art survey.

## Result table

Each row is one authored full scan. Error is the maximum absolute discrepancy from the eight authored sample truths, in signal units. A scan must export all eight samples to qualify for error comparison. Duration is total scheduled scan completion in ms; values do not include file writing. Timings are authored for the example and not independent of the prescribed schedule.

| offset condition | mode | exported samples | max abs error | duration ms |
| --- | --- | --- | --- | --- |
| constant | R0 | 8 | 0.0 | 90 |
| constant | R1 | 8 | 0.0 | 160 |
| constant | R2 | 8 | 0.0 | 130 |
| linear drift | R0 | 8 | 7.0 | 90 |
| linear drift | R1 | 8 | 0.5 | 160 |
| linear drift | R2 | 8 | 0.0 | 130 |
| within-group step | R0 | 8 | 8.0 | 90 |
| within-group step | R1 | 8 | 1.0 | 160 |
| within-group step | R2 | 8 | 4.0 | 130 |

There are no repeats, confidence intervals, noise tests, variable-duration scans or stochastic missing-value statistics. These rows do not prove a deployment advantage. A separate eight-case functional checklist covers first and last groups, shared endpoint identity, repeated packets, timestamp order rejection, and missing ending references. All eight match the prescribed export oracle. Two of the eight deliberately missing-reference fixtures export six of eight samples; they are excluded from the complete-scan error table, not counted as zero-error scans. No recovery-latency figure is available. R1 needs no R2 interpolation and remains the strong comparison for changing offset; R0 is the simpler choice when offset is constant. These are facts of this constructed apparatus only.
