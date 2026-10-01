# Internal traceability — synthetic DEMO only

These are internal source identifiers, not scholarly citations. The entire research evidence universe is `draft.md`, `implementation.md`, `results.csv`, and `notebook.md` in the specified paper-input directory. Skill references guide editing only and supply no facts about this raster protocol.

| Final manuscript location | Source | Preserved use |
|---|---|---|
| Disclosure, abstract, evaluation, conclusion | N1, N6; task.md | Original authored synthetic fixtures; no benchmark, publication, first-of-kind, significance or deployment claim |
| Introduction and Method opening | I1, N6 | 64 pointers; 4096 four-byte cells per tile; 1,048,576-byte payload; inherited immutable versions, root capture/copy, reference counting, sparse invalidation, checksums and atomic publication |
| Introduction two-tile example and Method second paragraph | I7, I2, I3 | a0/b0 → a1/b1; mixed intermediate IT root; SP private staging; unchanged tiles remain shareable |
| Method protocols | I2, I3 | FS staging and existing root swap; tagged immediate IT; SP manifest with base, target and changed set; target coherence rather than equal creation timestamps; no global wall-clock simultaneity |
| Method acknowledgement and coalescing | I4 | Acknowledge published root only; at most eight completed revisions of manifests; union touched coordinates and take target values; changed-back coordinates can remain |
| Method rejection and fallback | I5, N5; draft System | Pinned-base commit check; reordered staging; idempotent matching duplicates; conflicting duplicate rejection; size/checksum/range validation; visible coherent state on rejection; disconnect and late-packet rules; FS fallback; volatile scope |
| Method retention and Evaluation memory paragraph | I6, N1 | 512-byte root table; 4096-byte descriptors/counters; old plus replacement payload; dense pending can be full frame; no bounded old-reader lifetime; table excludes metadata and assumes one reader completes within one display cycle |
| Evaluation setup | N2, N3 | 120 roots; lossless data; identical schedule within workload/link pair; completion versus first byte; any prescribed interleaving criterion; three patterns, only sparse fast link; 32 packets and 20 ms; 64-packet run excluded; identical serialization/transport except selection/manifest; no compression, repetitions, uncertainty, stochastic model or CPU study |
| Table 1 | results.csv FS/SP rows | Eight rows, all original numerical fields, reordered only |
| Table 2 | results.csv IT rows | Four diagnostic rows, all original numerical fields; no coherence-preserving performance claim |
| Evaluation comparison prose | results.csv; I6, N3 | Sparse/moving constrained benefit; dense and fast-link reversals; preparation higher; retention grows with density; no component causal attribution |
| Evaluation functional suite | N4 | 28 oracle-matching manual traces, all named scenario categories, eight FS fallbacks, no recovery timing or demonstrated fallback byte advantage |
| Evaluation development variants | N5 | 2/6 missing-base-check failures; 1/6 early-ack failure; target-value coalescing and malformed-ID rejection; functional rather than timing ablations |
| Discussion | N1, N3–N6, I5–I6 | Conditional adoption; no crossover/adaptive selector evaluation; fallback separate; no implemented allocation-failure/process-crash tests; security/authentication/Byzantine behavior outside scope; no literature/deployment claims |

No new ratios, experiments, thresholds, literature, or timings were introduced. The explicit full-payload quantity can also be checked as 64 × 4096 × 4 = 1,048,576 bytes; it is supplied directly in I1.
