# Row Checks After Carrier Exchange: What Selective Focus Refresh Can Detect

**DEMO technical paper. All apparatus, events, observations, and timing values are constructed. No physical experiments or literature search were performed.**

## Abstract

After exchanging an imaging carrier, recovering its pose does not establish that every stored focus setting remains valid. We examine a selective refresh rule that checks one center in each of three rows and measures the outer sites only when the center change exceeds 8 µm. A deterministic nine-site construction separates exact global registration from local residual changes and compares this rule, ROW3, with full measurement, retained-map reuse, and a simpler row-shift correction. Across 24 paired invented exchanges, ROW3 accepts all nine centers in 12 events, versus 24 for full measurement and eight for row-shift correction. Its mean complete cycle is 21.83 s versus 25.33 s for full measurement, but two schedules take 28.05 s. The extra probes recover local changes when they share a triggered row; they cannot detect an isolated change elsewhere. This DEMO therefore identifies the spatial condition and motion costs governing selective refresh, without establishing physical feasibility, empirical performance, or novelty.

## 1. The gap between registration and local focus

A removable carrier lets an imaging station exchange several specimens together. Reusing their earlier focus settings is attractive because measuring every location consumes time. Yet repeatable seating and repeatable specimen height are different properties. Fiducials and datum tabs can recover the carrier's rigid pose and global plane while an individual specimen location still moves relative to that plane. The operation at issue is therefore the decision to retain or replace the local map after registration, rather than registration itself.

The proposed ROW3 rule samples the center of each row before deciding whether to remeasure that row's outer sites. This replaces a fixed nine-probe schedule with three checks plus conditional work. A center check only observes one location, however. A large change confined to an outer site may be absent from that observation. Conversely, a broad row displacement may be corrected by a simpler policy that applies the center's observed shift to every stored value in the row, without additional measurements.

These alternatives make the useful question narrower than whether three checks “guarantee focus.” We ask which changes conditional outer-site measurement actually recovers, and what its executed route costs. The contribution of this constructed analysis is an explicit connection between the sampling rule, its spatial failure condition, and complete attempt accounting. Geometry and policy records support that connection; they do not constitute an instrument validation or a claim of priority. The strong universal assertion in the working draft is contradicted by the complete records [S-DRAFT, S-FIELD].

## 2. A carrier whose legal centers do not imply clear paths

The declared carrier is 96 × 76 mm, with nine 18 × 14 mm apertures centered at x = −32, 0, 32 mm and y = −24, 0, 24 mm. Each contains a centered 8 × 6 mm imaging field. Site names combine southern, middle, or northern row S/M/N with western, center, or eastern column W/C/E. The origin is the carrier center, +x is east, and +y is north. Two lateral fiducials and three exposed datum tabs provide exact rigid xy registration and exact plane recovery in this model. Their common prescribed cost is 5.0 s: 2.0 s for fiducials and 3.0 s for datums [S-GEO].

[FIGURE_1]

**Figure 1. Legal endpoints can still require a raised transfer (DEMO).** The plan preserves all nine aperture and field locations. The fixed dock clip occupies x ∈ [−10,10], y ∈ [9,15] mm; expanding it by the shoe's 6 mm lateral half-width gives the dashed center keepout [−16,16] × [3,21] mm. The highlighted MC–NC segment crosses this region although neither endpoint does. The separate schematic height view identifies the 1.2 mm low underside, 3.4 mm clip top, and 4.4 mm raised underside. Its depth and vertical scale serve illustration; the plan uses one lateral scale. Fiducials and datums are distinct registration objects, not additional specimen sites.

A square 12 × 12 mm protective shoe surrounds the optical axis. At low travel its underside is at z = 1.2 mm, below the clip top at 3.4 mm. A straight center trajectory touching the expanded rectangle requires travel at z = 4.4 mm. Each intersecting segment incurs one complete raise/lower charge: 2 × 3.2/10 + 2 × 0.05 = 0.74 s. Counting intersections by segment avoids charging entry and exit twice. The nominal raised clearance is 1.0 mm; the construction is not certified collision protection. This geometry matters because changing the probe list also changes which transfers cross the obstacle.

## 3. Measurements, retained values, and commanded values

The stored local map is a shallow bowl, separate from the new plane:

$$b_j = 0.004x_j^2 + 0.005y_j^2. \tag{1}$$

Coordinates are in mm; the coefficients are in µm/mm² and b_j is in µm. For exchange e, the current global plane is

$$p_e(x,y) = a_e x + b_e y + c_e. \tag{2}$$

The plane coefficient b_e is distinct from stored value b_j. The true center height is p_e(x_j,y_j) + b_j + d_ej, where d_ej combines a row shift, a small site texture, and an optional eastern-site offset. A local reading after plane subtraction is m_ej = b_j + d_ej + n_ej. The fixed index-based probe error n_ej lies between −0.60 and +0.60 µm; it is not an empirical noise distribution [S-IMPL].

If q_ej is the commanded local value, true minus commanded focus error is

$$\mathrm{error}_{ej} = b_j + d_{ej} - q_{ej}. \tag{3}$$

The recovered plane cancels because its fit is exact. A center accepts when the error magnitude is at most 8.0 µm; an event accepts only when all nine centers accept. This criterion concerns field centers, not optical image quality or focus across an aperture.

Each policy starts from the same stored map independently for every event. PLANE retains q_j = b_j after common registration; it does not replace the old residual bowl with a flat surface. ALL9 measures SW, SC, SE, ME, MC, MW, NW, NC, NE and commands every measured value. ROW3 visits rows S, M, N, measuring C first. If |m_C − b_C| > 8.0 µm, it reuses that reading, measures W then E, and replaces all three values. Otherwise the whole row keeps its old values, including the measured center. Distinguishing “measured” from “updated” is necessary to reproduce its actual errors.

SHIFT3 measures SC, MC, NC and adds each observed center difference to all three old values in that row. It has no threshold or outer-site measurements. Thus ROW3 tests the value of measuring individual outer sites after a trigger; SHIFT3 tests whether a common row correction already suffices. Neither policy receives the event's construction label.

[FIGURE_2]

**Figure 2. A triggered row determines what ROW3 refreshes (DEMO).** Each panel shows the nine commanded-map states after one event, in the same north-up layout as Figure 1. Filled dots denote probes; teal fields are updated and pale fields retain their old values. The adjacent check values are measured center differences in µm, compared using strict magnitude >8. The error annotations concern SE in C01 and NE in C05. C01 triggers S, so its eastern-local change is measured and all nine centers accept. C05 triggers M while the extra change lies at NE: N retains its map and NE has 18.0 µm error. Both events use five probes and the same 22.17 s modeled cycle. The orange cross denotes center failure, not a measured alarm available to the controller.

Every nonempty local route starts and ends at PARK = (−40,−30) mm. Empty PLANE calibration has zero route distance. With straight travel at 80 mm/s and 0.75 s per probe, local calibration costs

$$T_{\mathrm{local}} = L_{\mathrm{local}}/80 + 0.75N_{\mathrm{probe}} + 0.74N_{\mathrm{raise}}. \tag{4}$$

All policies then acquire the nine centers in ALL9's serpentine order and return to PARK. Acquisition includes 340.0 mm travel, one raised transfer on the final return, and nine 0.4 s stops, totaling 8.59 s. Complete cycle time is

$$T_{\mathrm{cycle}} = 5.0 + T_{\mathrm{local}} + 8.59\ \mathrm{s}. \tag{5}$$

Acceleration, variable search duration, failure detection, recovery, export, and operator intervention are excluded. These are specified kinematic sums, not elapsed-time measurements [S-GEO, S-TRACE].

## 4. Paired cases and the limits of selective refresh

The fixed grid contains eight broad-row events B01–B08, eight eastern-local events E01–E08, and eight combined events C01–C08. Broad cases range from no large displacement to three changed rows. Eastern-local cases keep center checks small while adding an outer offset. Combined cases place the outer offset on the changed row in C01–C04 and on another row in C05–C08. Deterministic texture and probe error are shared whenever policies visit the same event/site. There are 24 exchanges evaluated four ways, yielding 96 paired runs and 864 nested center outcomes, not 96 independent exchanges [S-INPUT, S-FIELD].

**Table 1. Complete condition results for the fixed DEMO grid.** Event denominators are eight and center denominators are 72 in each row. Worst error includes every center; mean complete cycle includes all eight attempts, including failures. Displayed times are rounded to two decimals.

| Condition | Policy | Accepted events | Accepted centers | Worst error (µm) | Mean cycle (s) |
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

ALL9 accepts every event with worst error 0.60 µm, consistent with directly measuring each center. PLANE accepts only the quiet broad-row case. On broad-row events, SHIFT3 accepts the same eight events as ROW3 at a lower mean complete cost, 19.27 versus 24.03 s. The more elaborate conditional refresh therefore has no acceptance advantage on that subset. Its lower maximum center error does not alter this binary acceptance result.

ROW3's extra probes matter in the first four combined cases: once a row triggers, its outer readings recover the additional local offset, whereas copying its center shift cannot. The last four combined cases expose the limit. The changed row triggers correctly, but a different row's outer change remains unseen. Neither ROW3 nor SHIFT3 accepts any eastern-local case. These failures directly reject a universal guarantee from three row checks; they do not estimate the frequency of such changes in hardware.

[FIGURE_3]

**Figure 3. Acceptance and complete attempt costs across every constructed exchange.** The upper matrix shows all 96 policy/event outcomes; a filled circle accepts all nine centers and a cross denotes failure. The lower plot uses the same event order and shows every ROW3 cycle, with constant PLANE, SHIFT3, and ALL9 cycles as labeled reference lines. ROW3 markers retain the acceptance encoding. Group prefixes B, E, and C combine with case numbers 1–8 to identify every event; horizontal position is case order, not time. No failed attempt is removed and no uncertainty intervals are implied.

**Table 2. Complete all-attempt cost summary over the same 24 DEMO events.** Raised transfers are local-calibration counts. Cycle columns add the common 13.59 s to local time. All means include failures; editable CSVs retain source precision.

| Policy | Accepted events | Mean probes | Mean path (mm) | Mean raises | Mean local (s) | Cycle min / mean / max (s) |
|---|---:|---:|---:|---:|---:|---:|
| PLANE | 1/24 | 0.00 | 0.00 | 0.00 | 0.00 | 13.59 / 13.59 / 13.59 |
| ALL9 | 24/24 | 9.00 | 340.00 | 1.00 | 11.74 | 25.33 / 25.33 / 25.33 |
| ROW3 | 12/24 | 4.75 | 255.63 | 2.00 | 8.24 | 19.27 / 21.83 / 28.05 |
| SHIFT3 | 8/24 | 3.00 | 155.65 | 2.00 | 5.68 | 19.27 / 19.27 / 19.27 |

ROW3's mean local calibration is 29.83% shorter than ALL9's, but the complete-cycle reduction is only 13.83% because registration and acquisition remain. This all-attempt mean also includes 12 unsuccessful events; it is not useful-acquisition throughput. In B07 and B08, all rows trigger, producing nine probes along a 498.45 mm route with two raised transfers. ROW3 then takes 28.05 s, exceeding ALL9's 25.33 s despite equal probe counts. The sequence and return path, not probe count alone, determine the modeled cost [S-RUN, S-TRACE].

## 5. Interpretation and remaining work

The comparisons distinguish an observable row displacement from an unobserved local defect. SHIFT3 is sufficient for the constructed broad changes; ROW3 adds value when a local offset shares a row with a detectable center change. That is an opportunistic coverage condition, not a diagnostic test for every local disturbance. ALL9 supplies complete center coverage in this grid at a fixed modeled cost. Selecting among these policies requires information about the intended carrier family that the invented case counts cannot provide.

A physical study would need repeated seating trials to establish spatial correlations, a characterized autofocus metric, and image-level acceptance over the intended field area. Exact datum and xy recovery must be replaced by measured residual errors. Low-texture focusing, drift during acquisition, and hysteresis after raising also remain unmodeled. The nine-point surface is not a material deformation model; it supports no stress, modulus, or between-site prediction. No route optimization, extra-sentinel placement, or failure recovery has been implemented. Adding any of them would change the tested system and its cost model.

## 6. Conclusion

Selective row refresh changes which local values are measured after carrier exchange, but its coverage follows the trigger location. The constructed evidence supports recovering outer changes in triggered rows while retaining both missed local changes and route-dependent slow cases. It does not support calibration-free exchange or a universal focus guarantee. The result is a reproducible, bounded design comparison whose next evidential step is a physical carrier and image-quality study.

## Internal sources

[S-GEO] `apparatus_and_operations.md`. [S-IMPL] `construct_demo.py` and `implementation_notebook.md`. [S-INPUT] `data_v1/events.csv`. [S-FIELD] `data_v1/field_results.csv`. [S-RUN] `data_v1/run_results.csv`. [S-TRACE] `data_v1/probe_trace.csv`. [S-DRAFT] `rough_manuscript_v0.md`. All are the supplied constructed packet; no external references are claimed.
