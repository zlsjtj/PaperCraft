# Self-review: one revision after the preserved first draft

Only the designated local DEMO sources and the candidate PaperCraft entry with its required references/examples were used. No external feedback, independent agent review, web search, experiment or human approval occurred. first.md was saved once and remains unchanged; final.md is the single self-revision. Word/PDF generation and rendered-page acceptance were outside this task.

## Actual changes and editorial judgment

1. **Make the base do visible work in the abstract.** First: “We describe changed-tile patches assembled privately against a named, pinned base …”. Final: “We assemble changed-tile patches privately, sharing unchanged tiles from a named, pinned base …”. The second version says what depends on the base rather than merely naming it. The opening's full-snapshot credit and both negative cases remain. Cost: a slightly longer mechanism sentence.
2. **Connect acknowledgement to the next update.** First: “The client acknowledges only a root it has published.” Final precedes this rule with “The published root also determines which unchanged tiles a later patch may reuse,” and explains the potential first-packet acknowledgement error. This links a control field to the state it protects before presenting the 1/6 functional failure. It is a conditional explanation from the supplied mechanism, not an added failure trace. Publication validation now precedes later-update construction. Cost: the method grows and retains several exceptional paths because omitting them would change the operation.
3. **Let the valid baseline set the result comparison.** First placed IT's low coherent counts between the valid-method observation and the sparse gain. Final states before Table 1 that FS/SP qualify, compares their positive and negative cases continuously, then interprets IT separately. The table still contains every IT cell; its delay is explicitly diagnostic. Cost: the coherence qualification appears in the table note as well as in prose to prevent the fastest row from being misread.
4. **Use Discussion for the adoption decision.** First repeated the base-check and acknowledgement mechanism. Final asks when dependent assembly repays its cost, then separates history fallback from reader-retention limits. It explicitly avoids inferring a crossover threshold from four cases. Cost: the final Discussion is longer and “dependent assembly” still assumes the reader remembers the method.
5. **Tighten numerical semantics.** The table caption now states that preparation is a median and moves binary-unit/framing definitions beside the columns. Final also reports that p95 changes in the same direction as the median within each FS/SP pair. It labels assembly overhead as a plausible explanation, with no isolated causal measurement.

## Source-backcheck and verification

- Re-read implementation.md and notebook.md after the complete first draft, then located the pinned-base commit, publication-only acknowledgement, union-of-touched target values, eight-revision retention, invalid/incomplete/disconnected discard and full-snapshot fallback in the text.
- Both manuscripts retain all 12 results.csv rows, with every original result field checked cell by cell. The compressed case labels map unambiguously to the original workload/link identifiers in traceability.md.
- Preserved the full-snapshot coherence capability, IT's failed reader interleavings, the two negative timing cases, the single-reader memory assumption, functional fallback without recovery timing, 2/6 and 1/6 reconnect failures, finite prescribed schedules and untested failure/security domains.
- Recomputed only the stated arithmetic: 80.5% completion reduction and 93.4% wire reduction, both relative to FS in the constrained sparse case. No new timing, interpolation, confidence interval or experiment was generated.
- A whitespace-token count excluding Markdown table rows gives 1435 for first.md and 1541 for final.md, including headings and the short disclosure. The increase is intentional causal explanation, not global shortening.
- first.md SHA-256 remains 6284FEF825E13F6C8BA7FD116D62F613AFCB5053D018EA6F9BAB0F113915F403. checks.json records transcription checks and output hashes.

## Remaining limitations

The final text is still relatively dense in the protocol and table-caption passages. The single table preserves all values but has eight columns; only Markdown content and alignment were inspected, not a rendered print page. The engineering connection and comparison sequence are stronger in my self-reading, but no reader-comprehension, aesthetic, scientific novelty or acceptance result has been established. Both drafts remain synthetic editorial artifacts. No second self-revision was performed.
