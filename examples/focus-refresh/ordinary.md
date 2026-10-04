# DEMO — When Row Sentinels Can Support Focus-Map Reuse after Carrier Exchange

**Constructed technical case study. Zero physical experiments; no external literature search. All dimensions, observations, and times below belong to an invented evaluation packet.**

## Abstract

Exchanging a specimen carrier changes both its global pose and potentially its local focus map. Recovering the pose does not establish that stored settings remain valid at every specimen. This DEMO examines row-triggered map refresh in a nine-position carrier, comparing it with complete measurement, global registration alone, and a thresholdless row-shift baseline. A fixed grid contains 24 invented exchanges evaluated independently under all four policies. ROW3 accepts all eight broad-row cases, but none of eight eastern-local cases and only four of eight combined cases. It therefore accepts 12/24 events while reducing mean complete-cycle cost from 25.33 to 21.83 modeled seconds relative to ALL9. SHIFT3 is cheaper and equally successful on broad-row cases. Route geometry also makes ROW3 slower than ALL9 when every row triggers. The resulting contribution is a bounded mechanism analysis: selective refresh is useful only when sentinel observability and the cost of its particular route justify reuse. These constructed results establish neither empirical performance nor novelty.

## 1. Why global recovery is insufficient

A removable imaging carrier offers a convenient unit of exchange, but the reusable information has two different spatial scales. Fiducials and seating datums recover the coordinate frame of the carrier. A stored residual focus map describes departures from that frame at individual specimen positions. An exchange can preserve the first relationship while changing the second. Treating these two forms of repeatability as interchangeable risks commanding an old local height after apparently successful registration.

The initial draft proposed checking one center in each row and refreshing only rows with a large measured change. It provisionally described this as calibration-free and asserted that three checks guaranteed focus across all considered deformations [S-DRAFT]. The executable policy and complete records support a narrower question: when does a center-column sentinel reveal that its row needs fresh measurements? The answer depends on where the residual change occurs, not simply its maximum size.

This paper develops three connected elements of that question. First, it separates exact global registration from the local values actually commanded by four executable policies. Second, it connects a legal imaging endpoint to the clearance of the intervening head trajectory, retaining the cost of every raised transfer. Third, it reports acceptance and complete-cycle budgets together across the full paired case grid. These elements make the proposed shortcut inspectable, including its failures and a strong inexpensive baseline. They are analytical and implementation contributions within this DEMO; no priority claim or physical validation is implied.

## 2. Geometry, observations, and acceptance

The declared carrier is 96 × 76 mm, with east-positive x and north-positive y. Nine aperture centers lie at x = {−32, 0, 32} mm and y = {−24, 0, 24} mm. Row letters S, M, N and column letters W, C, E identify the centers. Each 18 × 14 mm aperture contains an 8 × 6 mm imaging field. The model evaluates best-focus height only at its center [S-GEO].

Two fiducials recover rigid xy pose; three exposed datum tabs recover the global plane. Both operations are exact here and together cost 5.0 s: 2.0 s for fiducials and 3.0 s for datums. Their detailed sensor paths are outside the local trace. The old residual map is retained at all nine centers; it is not replaced by a flat plane:

$$
b_j = 0.004x_j^2 + 0.005y_j^2 \qquad (1)
$$

Here x and y are in mm, and the coefficients are in µm/mm². The current global plane is

$$
p_e(x,y) = a_ex + b_ey + c_e. \qquad (2)
$$

Plane slopes have units µm/mm and the intercept has units µm; the coefficient b_e is distinct from stored value b_j. At a center, current height is p_e(x_j,y_j) + b_j + d_ej. The local change d_ej combines a row displacement, site texture, and an optional eastern-site displacement. A local reading after plane subtraction is m_ej = b_j + d_ej + n_ej, with deterministic observation error bounded by ±0.60 µm. This is not an empirical noise distribution [S-IMPL].

If q_ej is the commanded local value, true-minus-commanded focus error is

$$
\mathrm{error}_{ej} = b_j + d_{ej} - q_{ej}. \qquad (3)
$$

The plane cancels because recovery is exact. A center accepts when its absolute error is at most 8.0 µm; an event accepts only when all nine centers accept. Neither criterion measures full-field image quality.

[FIGURE_1]

**Figure 1. Geometry and clearance in the constructed apparatus.** (a) The proportional plan shows nine apertures and fields, two xy fiducials, three plane datums, park, the fixed clip, and the dashed center keepout. The arrow from MC toward NC crosses that keepout although both centers are legal. Decorative plate thickness is schematic. (b) An exaggerated section at x = 0 distinguishes low and raised shoe undersides from the clip top. The 1.0 mm nominal raised clearance is not certified collision protection. Source: S-GEO.

## 3. What each policy measures and commands

All policies start independently from the same old map for each event. PLANE performs common registration and retains q_j = b_j everywhere. Its name refers to the recovered global plane, not a zero local residual. ALL9 measures every center in the order SW, SC, SE, ME, MC, MW, NW, NC, NE and commands its reading at each site.

ROW3 processes rows S, M, N. In each row it first measures C and tests the strict condition |m_C − b_C| > 8.0 µm. If true, it reuses that center reading, measures W then E, and replaces all three row values. If false, it retains all three old settings, including the measured center's old setting. Thus measuring a sentinel is not synonymous with updating its command. The policy uses three, five, seven, or nine local measurements.

SHIFT3 visits SC, MC, NC and adds the observed center change to all three old values in each row: q_j = b_j + (m_C − b_C). It has no threshold and never measures an outer site. This baseline tests whether copying a common row displacement already obtains the claimed benefit without ROW3's triggered outer measurements [S-IMPL, S-TRACE].

[FIGURE_2]

**Figure 2. Decision logic and three actual records from the DEMO grid.** (a) ROW3's measured, triggered, and retained values are distinct. (b) Bars show true local changes, while open circles show observed center changes; the dashed line is +8 µm. All displayed changes are positive, so only the upper threshold is drawn. C01 triggers the southern row and measures its eastern disturbance. E01 and C05 retain the displayed rows despite eastern disturbances; in C05 the triggering broad change is in another row. These selected explanatory examples do not replace the full-grid evaluation. Sources: S-IMPL, S-FIELD.

## 4. Why the route belongs in the cost

The head's protective shoe is a 12 × 12 mm square. A fixed clip occupies x = [−10, 10] mm and y = [9, 15] mm, with its top at z = 3.4 mm. Expanding its footprint by the shoe's 6 mm half-width yields the closed center keepout [−16, 16] × [3, 21] mm. Boundary contact counts as intersection. The low underside is z = 1.2 mm; intersecting straight segments use a raised underside at z = 4.4 mm. Raising and lowering 3.2 mm at 10 mm/s, plus two 0.05 s settles, costs 0.74 s per intersecting segment [S-GEO].

Every nonempty local route starts at park (−40, −30) mm and returns there before acquisition. With local distance L, probe count N, and raised-transfer count R,

$$
T_{\mathrm{local}} = L/80 + 0.75N + 0.74R. \qquad (4)
$$

Distance is in mm and time in seconds. The common acquisition follows ALL9's serpentine ordering with departure from and return to park: 340.0 mm travel, one raised transfer, and nine 0.4 s stops. Its cost is 8.59 s. Consequently,

$$
T_{\mathrm{cycle}} = 5.0 + T_{\mathrm{local}} + 8.59. \qquad (5)
$$

PLANE has zero local distance. Acceleration, focus-search variability, failure detection, and recovery are excluded. These sums are kinematic budgets, not measured instrument times.

## 5. Complete paired evaluation

The fixed grid comprises eight broad-row cases B01–B08, eight eastern-local cases E01–E08, and eight combined cases C01–C08. Broad cases span zero through three substantially changed rows. Eastern cases add one eastern-site displacement while keeping sentinel changes small. Combined cases place the eastern disturbance on the changed row for C01–C04 and on another row for C05–C08 [S-INPUT]. Condition labels are construction metadata, unavailable to the controller.

Each policy receives the same preconstructed reading for a given event and site. The dataset contains 24 invented exchanges, 96 paired policy runs, 864 nested center results, and 474 local probe or return records. It contains no physical repeats or sampled carrier population. All failed attempts remain in the counts and arithmetic time means; no confidence intervals or significance tests are inferred from the field-row count. The complete exported records and timing sums were checked against both supplied tabular views.

**Table 1. All condition–policy results.** Each condition has eight events and 72 centers. Worst error covers every center; mean complete-cycle time includes all eight attempts, successful or unsuccessful. Constructed values only. Sources: S-FIELD, S-RUN.

| Condition | Policy | Accepted events | Accepted centers | Worst absolute error (µm) | Mean cycle (s) |
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

ALL9 accepts every event, with worst error 0.60 µm, reflecting the constructed observation bound. PLANE accepts only B01. ROW3 accepts all broad-row cases, but fails every eastern-local case. In E01 its southern sentinel observes only 0.15 µm change while the eastern center retains 12.65 µm error. The guarantee proposed in the draft therefore fails directly.

ROW3's four accepted combined cases explain its more limited advantage over SHIFT3. A triggered row causes both outer positions to be measured, so an additional eastern disturbance on that row is corrected. When the disturbance lies on another, untriggered row, it remains unseen. SHIFT3 accepts all broad-row cases but no combined or eastern-local cases: copying a center displacement cannot remove the extra eastern displacement. Its broad-row worst error is 2.00 µm, still within acceptance.

**Table 2. Complete all-attempt cost accounting.** Means cover the same 24 paired events for each policy. Local distance includes return to park. The final column gives minimum / mean / maximum complete-cycle seconds. Acceptance is reported alongside cost, without assigning usefulness to a failed attempt. Source: S-RUN.

| Policy | Accepted events | Mean probes | Mean local path (mm) | Mean raised transfers | Mean local time (s) | Cycle min / mean / max (s) |
|---|---:|---:|---:|---:|---:|---:|
| PLANE | 1/24 | 0.00 | 0.00 | 0.00 | 0.00 | 13.59 / 13.59 / 13.59 |
| ALL9 | 24/24 | 9.00 | 340.00 | 1.00 | 11.74 | 25.33 / 25.33 / 25.33 |
| ROW3 | 12/24 | 4.75 | 255.63 | 2.00 | 8.24 | 19.27 / 21.83 / 28.05 |
| SHIFT3 | 8/24 | 3.00 | 155.65 | 2.00 | 5.68 | 19.27 / 19.27 / 19.27 |

ROW3 reduces mean local cost by 29.83% relative to ALL9 over all 24 attempts, but the complete-cycle reduction is only 13.83% because registration and acquisition remain. Neither percentage is successful-throughput improvement. On the eight broad cases where both accept, ROW3 saves 5.13% of complete-cycle cost, whereas SHIFT3 saves 23.94%. On B07 and B08, ROW3 probes all nine centers yet costs 28.05 s against ALL9's 25.33 s. Its center-first traversal and two raised transfers offset the apparent benefit of adapting measurement count. ALL9 itself has one raised transfer on its return from NE; omitting that segment would understate its cost [S-TRACE].

[FIGURE_3]

**Figure 3. Full-grid coverage and the cost of ROW3's individual attempts.** (a) All 12 condition–policy groups report accepted events out of eight. (b) ROW3 shows every event in fixed order; crosses retain failed attempts. Horizontal references show constant complete-cycle costs and whole-grid acceptance counts for ALL9 and SHIFT3. The two 28.05 s ROW3 points exceed ALL9 despite measuring the same nine centers. All times are constructed sums, not experimental elapsed time. Source: S-RUN.

## 6. Implications and limits

The necessary condition exposed by these cases is spatial observability: a sentinel must respond to the changes for which its row is expected to be refreshed. Exact global recovery does not supply this property. Nor can a small center reading certify outer positions without a justified bound on within-row variation. The current model contains no such bound covering arbitrary local disturbances. Calling ROW3 calibration-free would additionally hide three mandatory local measurements and common registration.

SHIFT3 sharpens the design decision. For the supplied broad-row regime, transferring the measured shift is both sufficient and cheaper. ROW3's additional work buys coverage of local disturbances only when their row already triggers. This distinction is more informative than presenting average savings alone. A practical decision would require a defined carrier family and evidence about residual correlation, followed by acceptance criteria matched to the intended images.

The nine-point construction is not an elastic plate or optical image-formation model. It establishes no material response, aperture flatness, autofocus robustness, thermal stability, or retraction hysteresis. Real development would need seating trials, registration-error measurements, specimen-dependent focus validation, and checked trajectories. The nominal clearance is not a safety certification. No route optimizer, extra-sentinel search, detection-and-retry policy, or fallback-to-ALL9 procedure was implemented; their costs cannot be silently added or assumed away. A literature comparison is also absent, so novelty and superiority to published systems remain unassessed.

## 7. Conclusion

Within this constructed grid, row-triggered refresh offers conditional reuse rather than guaranteed carrier-wide focus recovery. Its 12/24 acceptance and route-dependent costs delimit that claim. The retained failures, strong SHIFT3 comparison, and complete timing budget identify what must be established before pursuing an instrument: observable local change, justified spatial reuse, and accepted images at a measured total cost.

## Internal source register

S-GEO: `apparatus_and_operations.md`. S-IMPL: `construct_demo.py`. S-INPUT: `data_v1/events.csv`. S-FIELD: `data_v1/field_results.csv`. S-RUN: `data_v1/run_results.csv`. S-TRACE: `data_v1/probe_trace.csv`. S-DRAFT: `rough_manuscript_v0.md`. All are frozen development-packet materials; no external references are claimed.
