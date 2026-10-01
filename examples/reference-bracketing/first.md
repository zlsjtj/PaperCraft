# Two-Well Reference Bracketing: Scheduled Scan Savings and a Step-Offset Limit

*Editorial DEMO. All apparatus descriptions, numbers and outcomes are authored for this exercise, not real measurements or an existing publication. They must not be cited as research evidence. No external sources or literature-priority claims are available.*

## Abstract

Reading a reference before every sample already addresses changing additive offset. We examine whether bracketing two samples with shared reference endpoints can reduce that acquisition burden. In an authored eight-well fixture, the bracketed mode uses thirteen acquisitions instead of sixteen and completes its prescribed schedule in 130 rather than 160 ms. Its maximum absolute error is zero under linear drift, compared with 0.5 signal units for the per-sample reference mode. A within-group offset step reverses this advantage: errors are 4.0 and 1.0, respectively. The controller withholds each sample pair until its closing reference arrives, making complete reference intervals a condition of export.

## 1. Introduction

An optical scan visits eight numbered sample wells using one sensor. Reference subtraction is already available, as are the scan order, reference well and sensor firmware. The sensor reports arbitrary signal units; these do not establish concentration, biological properties or temperature. The reference contains a fixed optical standard, and the evaluator knows the authored sample truths.

A reference taken only before the scan can suffice when offset remains constant. Taking another before every sample already handles the stipulated time-varying additive offset, so providing reference support alone is not the unresolved problem. We instead ask what is gained and lost by placing two sample acquisitions between reference endpoints. The resulting comparison concerns scheduled acquisition cost and correction error under specified offset shapes. It also requires an export policy for readings whose closing reference is not yet available.

## 2. Method

All modes retain the same sample order and electronics. R0 subtracts one initial reference from all eight readings. R1 subtracts the reference acquired immediately before each sample. R2 places a reference immediately before and after each group of two samples, interpolating linearly between those reference values at the sample acquisition timestamps. These timestamps denote acquisition starts, and every acquisition has the same prescribed duration. Adjacent groups share an endpoint within a scan; a scan's ending reference is not reused in a later scan.

R2 therefore requires five reference acquisitions alongside eight sample acquisitions, compared with one reference for R0 and eight for R1: nine, sixteen and thirteen total acquisitions, respectively. Interpolation is existing arithmetic, not a new estimator. Its use connects each sample correction to both endpoints, so the controller cannot export that correction when the sample first arrives.

R2 stores both readings privately until the ending reference becomes available. Queue ownership prevents export of an incomplete pair; if either endpoint is missing, the group is marked unavailable rather than filled from the preceding group's reference. This work preserves the meaning of a bracketed correction at the export boundary. It does not make two endpoints sufficient to reconstruct an offset step inside the group, and queue ownership has not been timed separately.

## 3. Results

Table 1 reports one authored full scan per row. Error is the maximum absolute discrepancy from the eight sample truths, in signal units. Only scans exporting all eight samples qualify. Duration is scheduled scan completion, excluding file writing; the authored timings follow the prescribed schedule and are not independent performance measurements.

*Table 1. Complete authored scans under three offset conditions.*

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

The constant-offset case favors the simpler R0: all modes have zero error, while R0 finishes in 90 ms. Under linear drift, R2 improves on R1's 0.5 error while using three fewer acquisitions and 30 ms less scheduled time. The step case prevents treating that pairing as a general advantage. R1 has error 1.0, whereas R2 reaches 4.0 despite retaining the shorter schedule. R0's errors of 7.0 under drift and 8.0 under the step also show why it is not the decisive changing-offset comparison.

A separate eight-case functional checklist covers first and last groups, shared endpoint identity, repeated packets, timestamp order rejection and missing ending references. All cases match the prescribed export oracle. Two deliberately missing-reference fixtures export six of eight samples. They are excluded from the complete-scan error table, not assigned zero error; no recovery-latency figure is available.

## 4. Discussion and Conclusion

The bracketed mode offers a conditional tradeoff: it spends fewer acquisitions than per-sample referencing, but correction depends on what happens between its endpoints. R1 needs no R2 interpolation and remains the strong comparison for changing offset; R0 remains the simpler constant-offset choice. Delaying export protects the bracket's completeness without resolving its step sensitivity.

There are no repeats, confidence intervals, noise tests, variable-duration scans or stochastic missing-value statistics. The exercise provides neither independent hardware novelty nor a prior-art survey, and these rows do not prove a deployment advantage. Within this constructed apparatus, the useful result is an explicit choice among acquisition budget, offset behavior and whether a complete correction can be exported.
