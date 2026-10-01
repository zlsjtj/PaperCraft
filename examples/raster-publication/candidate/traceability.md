# Internal traceability

These identifiers refer only to the supplied local DEMO files. They are not scholarly citations. No outside research source or skill-example measurement entered the raster manuscript.

| Manuscript claim or condition | Local source | Final location |
|---|---|---|
| Synthetic fixtures, no measured/deployed/significant result | task.md; [N1], [N3], [N6] | Disclosure; Evaluation opening; Discussion |
| 64 tiles × 4096 four-byte cells; 1,048,576-byte full payload | [I1] | Method opening |
| Immutable tile versions, atomic roots, root capture and inherited facilities | [I1], [N6] | Introduction second paragraph |
| FS and SP both stage and publish; IT installs changed tiles immediately despite target tags | [I2], [N2] | Abstract; Introduction; Method opening; Evaluation |
| Pin named visible base; private pending root; all replacements validated before publication | [I2], [I3], [I5] | Method second/third paragraphs |
| A/B transition a0,b0 → a1,b1 with C unchanged; revision 8 tile may remain in root 11 | [I7], [I3] | Introduction example; Method second paragraph |
| No reader wait for packets; no wall-clock synchronization among clients | [I3] | Method third paragraph |
| Pinned-base commit, matching/conflicting duplicates, checksum/size/range validation, late messages, invalid/incomplete/disconnect discard | [I2], [I5], [N5]; draft.md parser description | Method third paragraph |
| Acknowledgement only after publication; at most eight completed manifests; missing/wrong/unverifiable base uses FS | [I4], [I5], [N4] | Method fourth paragraph |
| Coalescing takes coordinate union and target value once per coordinate; reverted tiles may remain | [I4], [N5] | Method fourth paragraph |
| First-packet acknowledgement could create dependence on an unpublished client root | Explanation from [I2], [I4], [N5], not a new observation | Method fourth paragraph |
| 512-byte root table; 4096-byte pending descriptors/reference counters; old/new tile retention; dense pending payload may reach full frame | [I6] | Method final paragraph |
| Same 120 target roots and schedules, lossless values; completion versus reader-interleaving coherence; finite schedules | [N2] | Evaluation opening; Table 1 |
| Three patterns, only sparse fast-local case; fixed 32 packets/20 ms; excluded 64-packet exploration; unchanged transport except selection/manifest; no compression | [N3]; draft.md | Evaluation second paragraph |
| All 12 numeric rows including p95, preparation and retention | results.csv | Table 1; Evaluation comparisons |
| Binary units, wire framing, payload-only memory, one reader released within one display cycle | [N1], [I6] | Table caption; Discussion |
| 28 functional traces and named edge cases; eight fallback traces; no recovery timing or promised fallback savings | [N4] | Evaluation last paragraph |
| Missing base check fails 2/6; first-packet acknowledgement fails 1/6 after coalescing; functional, not timing ablations | [N5] | Evaluation last paragraph |
| Volatile state; no allocation-failure/process-crash tests; security/authentication/Byzantine scope | [I5], [N5] | Discussion final paragraph |
| No novelty survey, universal novelty, production or statistical-significance assertion | [N1], [N3], [N6] | Abstract; Discussion |

## Table label mapping

- `4 / constrained` = `sparse_4_tiles,constrained`.
- `24 / constrained` = `moving_24_tiles,constrained`.
- `60 / constrained` = `dense_60_tiles,constrained`.
- `4 / fast local` = `sparse_4_tiles,fast_local`.
- `Coherent / total` preserves both source columns as numerator/denominator.
- `Median ms`, `p95 ms`, `Wire KiB`, `Retained MiB`, `Prepare ms` preserve `median_completion_ms`, `p95_completion_ms`, `median_wire_KiB`, `peak_retained_payload_MiB`, `median_prepare_ms`, respectively.

## Derived arithmetic

- Full payload: 64 × 4096 × 4 = 1,048,576 bytes.
- Sparse constrained completion reduction: (87 − 17) / 87 × 100 = 80.459770…%, rounded to 80.5%.
- Sparse constrained wire reduction: (1026 − 68) / 1026 × 100 = 93.372319…%, rounded to 93.4%.
- “p95 improves” compares FS→SP 106→31 and 110→74; “worse p95” compares 111→120 and 3.1→3.9. No new percentile was estimated.

No figure was required. No symbolic threshold, measured crossover, isolated component speedup or recovery statistic was derived. All key limitations stay in the manuscript, rather than relying on this file to qualify it.
