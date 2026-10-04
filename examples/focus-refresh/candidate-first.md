# Selective row refresh after carrier exchange: sentinel visibility and travel cost in a constructed imaging study

**DEMO — all apparatus, exchanges, observations and timings are constructed. Zero physical experiments were performed.**

## Abstract

Exchanging an imaging carrier requires recovering both its global pose and its local focus settings. Exact registration of the carrier does not establish that every specimen remains at its previous residual height. We examine selective row refresh: measure the center of each row, retain unchanged rows, and probe both outer positions when a center exceeds a change threshold. A deterministic nine-position DEMO compares this ROW3 policy with reusing the old map, measuring every position, and applying each measured center displacement uniformly across its row. All four policies share 24 constructed exchanges and a complete route-dependent timing model. The simpler displacement policy accepts all eight broad-row cases at 19.27 s per cycle; selective refresh costs 24.03 s on that subset. Selective refresh additionally accepts four combined cases when the isolated change falls in the refreshed row, but misses changes elsewhere. Across all cases it accepts 12/24 events versus 24/24 for full measurement, and its densest updates exceed the full-measurement cycle time. The DEMO identifies a conditional use for row refresh, not calibration-free exchange, physical performance or a universal focus guarantee.

## 1. Reusing a map requires knowing what changed

A removable carrier allows an imaging station to exchange several specimens together. Once it is reseated, recovering lateral position and overall tilt can restore a common coordinate frame, yet an individual specimen can still have a different local height. Reusing the old focus map therefore requires a decision about spatial change, rather than merely a successful registration operation.

The policy considered here checks one center in each of three rows. A sufficiently large change causes the controller to measure that row's remaining two centers; otherwise the entire row retains its old settings. The concrete advantage sought is avoiding measurements at locations whose stored settings remain useful. The central difficulty is visibility: an outer location can change without moving the center that decides whether the row is refreshed. Figure 1 makes this distinction using two actual cases from the constructed record.

A fair comparison must also include a simpler use of the same three observations. Applying the measured displacement uniformly across a row already compensates for coherent row motion without measuring its outer positions. Selective refresh must therefore justify its extra probes through cases where individual outer measurements matter. We evaluate that remaining question together with the cost of physically visiting the selected positions. The contribution of this exercise is an explicit conditional comparison and reproducible accounting, not a claim that the controller or mechanism is novel. No external literature search or physical validation has been performed [S-IMPL, S-INPUT].

[FIGURE_1]

**Figure 1.** Sentinel visibility in two constructed combined-change events. Each panel contains all nine centers at their carrier coordinates. Blue bands mark the row triggered by its center; blue rings identify probes, while coral diamonds identify the added eastern-local displacement. C01's extra displacement lies in the refreshed southern row; C05's lies at unrefreshed NE. ROW3 accepts 9/9 and 8/9 centers, respectively, despite using five probes in each. Values shown beside sentinels are observed changes relative to the stored residual; NE's 18.0 µm is the remaining focus error, not probe noise [S-FIELD, S-TRACE].

## 2. What the controller measures and commands

The carrier spans 96 × 76 mm, with east and north defining positive x and y. Its nine centers lie at x = {−32, 0, 32} mm and y = {−24, 0, 24} mm. Row names S, M and N combine with columns W, C and E. Each 18 × 14 mm aperture contains a centered 8 × 6 mm acquisition field. Only the best-focus height at each field center is modeled; neither the complete field nor the aperture is assumed flat [S-GEO].

Two carrier fiducials at (−43, −34) and (43, −34) mm provide exact rigid xy registration. Three exposed datum tabs at (−44, 34), (44, 34) and (0, −34) mm provide an exact global plane. Their prescribed budgets are 2.0 and 3.0 s. These operations remove the recorded exchange pose but do not replace the stored nine-center residual map. For center j, that map is

$$b_j=0.004x_j^2+0.005y_j^2. \tag{1}$$

Here x and y are in millimeters and the coefficients are in µm/mm². The current event's recovered plane is

$$p_e(x,y)=a_ex+b_ey+c_e. \tag{2}$$

The plane coefficients a_e and b_e have units µm/mm and c_e has units µm; b_e is distinct from stored value b_j. True height is p_e(x_j,y_j)+b_j+d_ej, where d_ej combines a row shift, small site texture and an optional eastern-local displacement. A probe returns m_ej=b_j+d_ej+n_ej after plane subtraction. The deterministic probe error is bounded by ±0.60 µm. For a commanded residual q_ej, true-minus-commanded focus error is

$$\mathrm{error}_{ej}=b_j+d_{ej}-q_{ej}. \tag{3}$$

The plane cancels because its recovery is exact. Center acceptance requires |error_ej| ≤ 8.0 µm; event acceptance requires all nine centers to pass [S-GEO, S-FIELD].

PLANE uses q_j=b_j with no local measurements. Despite its name, it retains the nonzero local bowl in Eq. (1). ALL9 measures every center and commands q_j=m_j. ROW3 visits rows S, M and N, first measuring C. If |m_C−b_C|>8.0 µm, it reuses that reading, probes W then E, and replaces all three row settings. Otherwise it retains all three old values, including the measured center's old value. A measurement alone is thus not an update. SHIFT3 instead probes SC, MC and NC and commands b_j+(m_C−b_C) throughout each row, with no threshold or outer probe [S-IMPL].

These choices distinguish observation from inference. A triggered ROW3 row obtains separate measurements at all three centers, while SHIFT3 infers its outer corrections from a center reading. An untriggered ROW3 row acquires no evidence about an isolated outer change. In C01, SC's observed change is 11.75 µm, so measuring SE captures the extra eastern displacement. In C05, MC triggers at 12.85 µm, but NC changes by only 2.10 µm; NE remains unmeasured and retains an 18.0 µm error. This is a visibility failure, not imperfect removal of the global plane.

## 3. Probe count is not the complete cost

The dock contains a fixed clip with footprint [−10, 10] × [9, 15] mm and top z=3.4 mm. The imaging head has a square 12 × 12 mm protective-shoe envelope. Its nominal low underside is z=1.2 mm, so low-travel center paths must avoid [−16, 16] × [3, 21] mm. None of the nine centers lies inside this rectangle. Nevertheless, a straight segment between valid centers may cross it, as Figure 2 shows.

[FIGURE_2]

**Figure 2.** Geometry behind raised-transfer cost. The plan uses the specified carrier coordinates and shows the complete three-sentinel local route, including its return to PARK. Both MC→NC and NC→PARK intersect the center keepout and each incurs one raised transfer. The x=0 section distinguishes the clip footprint from the shoe envelope and shows its underside raised from 1.2 to 4.4 mm. Vertical and lateral scales differ in the section. Fiducials and datum tabs are registered separately; PARK is a motion state, not a tenth specimen. Clearance is nominal, not certified [S-GEO, S-TRACE].

Every intersecting segment, including boundary contact, uses a raised underside of 4.4 mm. Raising and lowering each traverse 3.2 mm at 10 mm/s with two 0.05 s settles, totaling 0.74 s per segment. This nominal envelope model does not certify collision safety. All nonempty local routes start and end at PARK=(−40,−30) mm; PLANE contributes zero local route distance. With local route length L, probe count N and intersecting-segment count R,

$$T_{\mathrm{local}}=L/80+0.75N+0.74R. \tag{4}$$

Lengths are in millimeters and time in seconds. The 0.75 s probe stop includes measurement and local settling; lateral speed is 80 mm/s with acceleration excluded. ALL9 follows SW→SC→SE→ME→MC→MW→NW→NC→NE. Every policy then performs that same acquisition route, including departure from and return to PARK: 340 mm, one raised transfer and nine 0.4 s stops. Acquisition therefore costs 8.59 s, and

$$T_{\mathrm{cycle}}=5.0+T_{\mathrm{local}}+8.59\ \mathrm{s}. \tag{5}$$

Neither common operation is a per-probe charge. No failure detection, retry, fallback, operator intervention or export cost is included [S-GEO, S-RUN].

## 4. Paired results on the complete fixed grid

The input fixes eight broad-row cases, eight eastern-local cases and eight combined cases before scoring. Broad-row cases span zero to three changed rows. Eastern-local cases perturb one eastern site while center checks remain small. Combined cases place an eastern perturbation in the changed row for C01–C04 and in another row for C05–C08. These construction labels are unavailable to the controller. Texture and probe error follow deterministic index formulas, with no random draws [S-INPUT, S-IMPL].

Each policy independently starts from the same stored map on every event and receives identical readings for shared event/site probes. The records contain 24 exchanges, 96 paired policy runs and 864 nested center results, not 96 independent exchanges or 864 physical repetitions. Table 1 retains every condition/policy group, and Figure 3 exposes the individual events. All time means include failures.

[TABLE_1]

**Table 1. Complete condition results (constructed DEMO).** Event counts have denominator 8 and center counts denominator 72. Worst errors and mean full-cycle times include every attempt.

| Condition | Policy | Events accepted | Centers accepted | Worst error (µm) | Mean cycle (s) |
|---|---|---:|---:|---:|---:|
| Broad row | PLANE | 1/8 | 33/72 | 18.70 | 13.59 |
| Broad row | ALL9 | 8/8 | 72/72 | 0.60 | 25.33 |
| Broad row | ROW3 | 8/8 | 72/72 | 0.70 | 24.03 |
| Broad row | SHIFT3 | 8/8 | 72/72 | 2.00 | 19.27 |
| Eastern local | PLANE | 0/8 | 64/72 | 25.00 | 13.59 |
| Eastern local | ALL9 | 8/8 | 72/72 | 0.60 | 25.33 |
| Eastern local | ROW3 | 0/8 | 64/72 | 25.00 | 19.27 |
| Eastern local | SHIFT3 | 0/8 | 64/72 | 24.50 | 19.27 |
| Combined | PLANE | 0/8 | 44/72 | 38.00 | 13.59 |
| Combined | ALL9 | 8/8 | 72/72 | 0.60 | 25.33 |
| Combined | ROW3 | 4/8 | 68/72 | 20.70 | 22.19 |
| Combined | SHIFT3 | 0/8 | 64/72 | 23.85 | 19.27 |

SHIFT3 already accepts every broad-row case, with a 19.27 s cycle versus ROW3's 24.03 s mean and ALL9's 25.33 s. Its worst center error, 2.00 µm, remains below the acceptance limit. Thus broad-row success alone does not justify selective outer measurements. PLANE accepts only the quiet B01 case, demonstrating that common registration alone is insufficient even in this favorable model.

The extra measurements have a narrower benefit. ROW3 accepts C01–C04 because their eastern changes fall in triggered rows; SHIFT3 accepts none of the combined cases. Moving the local change outside the triggered row removes that benefit: ROW3 fails C05–C08 and all eastern-local cases. ALL9 accepts 24/24 events with worst error 0.60 µm, as expected when every commanded value differs from truth only by the bounded probe error. These outcomes do not establish a guarantee for unmeasured positions.

[FIGURE_3]

**Figure 3.** Complete paired event outcomes and modeled cycle times. The upper matrix records all 96 event/policy acceptance decisions. The lower plot shows every ROW3 cycle and the three constant comparator times on the same event order. Crosses preserve failed events; B07–B08 show accepted ROW3 cycles slower than ALL9. There are no empirical repetitions, uncertainty intervals or omitted failures [S-RUN].

[TABLE_2]

**Table 2. All-attempt operational cost over the same 24 constructed events.** Means include unsuccessful events; cycle ranges are minima and maxima over this fixed grid.

| Policy | Accepted events | Mean probes | Mean local path (mm) | Mean raised transfers | Mean local time (s) | Cycle min / mean / max (s) |
|---|---:|---:|---:|---:|---:|---:|
| PLANE | 1/24 | 0.00 | 0.00 | 0.00 | 0.00 | 13.59 / 13.59 / 13.59 |
| ALL9 | 24/24 | 9.00 | 340.00 | 1.00 | 11.74 | 25.33 / 25.33 / 25.33 |
| ROW3 | 12/24 | 4.75 | 255.63 | 2.00 | 8.24 | 19.27 / 21.83 / 28.05 |
| SHIFT3 | 8/24 | 3.00 | 155.65 | 2.00 | 5.68 | 19.27 / 19.27 / 19.27 |

ROW3's mean local calibration budget is 29.83% below ALL9, but its mean complete cycle is only 13.82% shorter. Both percentages describe all attempts, including twelve failures, rather than useful acquisition throughput. In B07 and B08, all rows trigger: ROW3 travels 498.45 mm and raises twice, versus ALL9's 340 mm and one raise. Equal nine-probe counts then yield 28.05 versus 25.33 s, a 10.74% cycle penalty. The return segment matters: even ALL9 has one raised transfer. Fewer probes cannot by themselves establish a faster usable cycle.

## 5. Implications and limits

The comparison suggests a deployment question rather than a universally preferred policy. When changes are sufficiently coherent within rows, SHIFT3's simpler displacement correction is already adequate on this grid. ROW3 adds value when a sentinel triggers a row containing otherwise unmodeled local variation. An isolated change elsewhere remains invisible, and dense refresh loses its timing advantage. Choosing among these policies therefore requires evidence about the spatial pattern of actual changes and the cost of detecting or recovering failures.

Those quantities are not supplied here. The nine-point surface is not an elastic-plate model, and no material properties or between-center behavior can be inferred. Exact datum and xy recovery, fixed measurement time and bounded deterministic noise omit real autofocus texture dependence, thermal drift, hysteresis and timing variability. A physical study would need repeated seating trials, measured deformation envelopes, trajectory validation and image-level acceptance. No route optimizer, extra-sentinel design or recovery policy was implemented. Accordingly, neither novelty nor unattended-operation readiness follows from these constructed results.

## 6. Conclusion

Selective row refresh changes where the controller spends local measurements after common registration. Its benefit is conditional: direct outer measurements recover some local changes that uniform row correction misses, but only when the center triggers that row. The full paired DEMO also shows that visiting all nine centers adaptively can cost more than a fixed nine-center schedule. Sentinel visibility, acceptance and complete travel cost must therefore be evaluated together before map reuse can be justified on a physical instrument.

**Source note.** S-GEO: apparatus and operation record; S-IMPL: deterministic generator; S-INPUT: all 24 input events; S-FIELD: all 864 center results; S-RUN: all 96 run summaries; S-TRACE: complete local operation trace. These internal sources are constructed and do not substitute for experimental or literature evidence.
