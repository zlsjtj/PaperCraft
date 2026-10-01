# Internal source traceability

These are identifiers in the supplied DEMO notes, not scholarly citations. The mapping covers both manuscript versions; section references below use final.md.

| Manuscript content | Supplied source | Use and evidence limit |
|---|---|---|
| DEMO disclosure and absence of real measurements | task.md; [N1] | Applies to every number, trace, and comparison. |
| Existing immutable roots, local reader capture, atomic publication, root copying, reference counts, invalidation, checksums | [I1]; [N6] | Inherited application mechanisms, not newly proposed primitives. |
| 64 tiles, 4096 four-byte cells each; 1,048,576-byte payload | [I1] | Configuration-specific size, not a scale study. |
| FS/IT/SP definitions and target tags | [I2] | Implementation names; FS and SP share the existing publication operation. |
| Coherence means target-root agreement, with legitimate old unchanged tile versions | [I3] | No requirement for uniform creation timestamps or simultaneous client display. |
| Two-tile mixed-view illustration | [I7]; [I3] | Semantic example only, no additional timing result. |
| Acknowledgement after publication, eight-revision manifest limit, touched-coordinate union, target values | [I4] | Coalescing is not a minimal-difference compressor. |
| Wrong/unavailable/unverifiable base, rejection, duplicate behavior, reordering, disconnect, stale-message protection | [I5]; [I2]; [N5] | Volatile display consistency; no durable crash-recovery or security guarantee. |
| 512-byte pointer table and 4096-byte descriptor/reference overhead; retention and preparation costs | [I6] | Payload table excludes metadata; no bound for stalled readers. |
| Every table cell | results.csv | All 12 source rows retained, including negative comparisons. Median/p95 share one table column without changing values. |
| Wire/payload units and framing | [N1] | Binary KiB/MiB; framing included in wire bytes. |
| Completion endpoint, coherence criterion, same 120 targets, finite interleavings | [N2] | Completion is packet application/staging; IT cannot serve as a coherence-preserving performance baseline. |
| Three tile patterns, sparse-only fast local, fixed 32-packet/20-ms settings, excluded 64-packet exploration | [N3] | No repeated sampling, confidence intervals, loss-model study, or microarchitecture analysis. |
| No compression | draft.md | A stated comparison condition, not a newly performed experiment. |
| 28 functional traces, listed case categories, eight FS fallbacks | [N4] | Separate from timing rows; no recovery-latency summary or sparse-saving claim on fallback. |
| Two of six failures without base checks; one of six with early acknowledgement; tile-ID validation | [N5] | Functional failures, not timing ablations. |
| Missing allocation/crash tests; security/authentication/Byzantine scope | [N5] | Explicit unimplemented or excluded areas. |
| No first-of-kind or publication-novelty claim | [N1]; [N6] | No supplied literature survey; no outside sources consulted. |

## Derived quantities

- Sparse constrained-link SP wire reduction relative to FS: (1026 - 68) / 1026 × 100 = 93.4% after rounding.
- Sparse constrained-link SP median completion-delay reduction relative to FS: (87 - 17) / 87 × 100 = 80.5% after rounding.
- These are arithmetic summaries of authored fixtures, not additional measurements.

## Interpretation boundary

The final paper's three-part framing and its description of a transfer/staging tradeoff are editorial synthesis of [I2]–[I6] and the fixed table. The explanation that preparation work is consistent with latency costs is explicitly qualified; no causal timing ablation is supplied. No automatic FS/SP threshold is derived. The strong FS comparison, IT failures, fallback costs, and limitations are preserved.
