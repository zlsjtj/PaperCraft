> **DEMO:** Original synthetic editorial-evaluation material. All numerical results are authored fixtures, not measurements from real experiments or a publication.

# Staging Base-Referenced Tile Patches for Coherent Raster Updates

## Abstract

An environmental dashboard can receive changed tiles quickly while briefly showing a raster that the producer never published. Staging a complete snapshot already prevents this problem, but transfers unchanged data. We describe staged patches that name a base revision, retain its unchanged tiles, and publish replacements together after validation. The mechanism extends an existing immutable-root renderer; neither dirty-tile tracking nor atomic publication is new. In fixed synthetic fixtures, staged patches reduce median completion delay from 87 to 17 ms for four changed tiles on a constrained link, while retaining coherence at every prescribed reader interleaving. They are slower than full snapshots for dense changes and for sparse changes on a fast local link. The resulting case is conditional: base-referenced staging can reduce transfer while preserving coherent display, provided its base remains available and preparation cost does not erase the benefit.

## 1. Transfer Less Without Showing an Unpublished Raster

A dashboard displays a committed raster revision, not merely a collection of recently received tiles. Suppose revision 10 contains tile versions a0 and b0, and revision 11 needs a1 and b1. Installing a1 immediately while b1 is delayed exposes (a1, b0), which belongs to neither revision. Attaching revision 11 to each packet does not prevent this mixture. The example illustrates the operation; it is not a timing observation.

The existing service already supplies the essential rendering abstraction: an immutable root containing 64 tile-version pointers, captured once per display frame. Each tile contains 4,096 four-byte cells, yielding a 1,048,576-byte full payload. Root copying, reference counting, sparse invalidation, checksums, and atomic local publication predate the transfer protocol. Raster values are assumed computed; this work does not evaluate their environmental accuracy.

Full-snapshot staging provides the strongest simple comparison because it already preserves root coherence. The remaining question is whether transferring only changed tiles can preserve that behavior at lower completion delay and retained payload. Our design ties a patch to a particular acknowledged base and keeps replacement tiles private until a complete target root can be published. Necessary protocol work concerns the validity of that base across delayed packets, coalesced revisions, and reconnection. The evaluation asks when these additional operations pay for themselves, rather than treating coherence alone as an advance over snapshots.

## 2. Constructing and Publishing a Target

We compare three implementations. Full snapshot (FS) stages an entire raster, validates its packets, and switches the visible root. Immediate tiles (IT) transfers changed tiles with a target revision tag and installs each pointer on arrival. Staged patch (SP) transfers a manifest naming the base, target, and changed-tile set. The client pins its visible base and builds a private pending root from shared unchanged tiles and validated replacements. FS and SP use the renderer's existing atomic root swap.

Returning to the two-tile example, SP leaves (a0, b0) visible while a1 is pending. Only after both replacements validate can a new reader capture (a1, b1). An unchanged third tile can be shared from the base. Coherence means matching the producer's target root, not assigning every tile the same creation revision: a target at revision 11 may legitimately retain a tile created at revision 8. Display readers do not wait for pending packets, although they may continue to see an older coherent revision. The protocol does not synchronize every client's displayed revision at the same wall-clock instant.

The server retains manifests for at most eight completed revisions in this configuration. A client acknowledges only the root it has published, and subsequent patches use that acknowledged revision when available. To coalesce several revisions, the server unions their touched coordinates and sends each coordinate's value from the target root. Sending an intermediate value would not reconstruct that target. A tile that changes and then returns to its original bytes may remain in this union; correctness does not imply minimal differences.

Before publication, a commit is checked against the pinned base. Out-of-order packets may be staged for their named target; matching duplicates are idempotent, whereas conflicting duplicates reject the patch. Size, checksum, and tile-range checks reject invalid input. Incomplete or invalid pending state is discarded while the last coherent root stays visible. Disconnect also discards uncommitted state, and late valid packets must not alter a newer visible root. A missing, incorrect, or unverifiable acknowledged base triggers FS fallback. These rules protect volatile display state; they do not constitute durable transaction or crash recovery.

Staging retains resources while readers finish. A pending root needs a 512-byte pointer table and 4,096 bytes of descriptors and reference counters, in addition to payload. SP retains old tiles plus replacements; FS retains an old and a new full frame. Dense SP updates can require a full frame of pending payload. Old-reader pinning has no proven lifetime bound, so a stalled reader can invalidate the reported memory interpretation.

## 3. Evaluation Design and Fixed Results

All values in Table 1 are synthetic inputs, not benchmark output. Each row uses the same 120 target roots and lossless values, with the same packet schedule within each workload/link pair. Completion delay runs from producer target publication until all required packets have been applied or staged; it is not first-byte latency. Coherence counts runs with no non-target mixed root at any prescribed reader interleaving from request to completion. This finite criterion does not cover every possible schedule.

Queue capacity and retry deadline are fixed at 32 packets and 20 ms. An earlier 64-packet exploratory run is excluded. Serialization and transport are identical except for required payload selection and manifest handling; no compression is enabled. There is one fixed schedule per case, with no repetitions, confidence intervals, stochastic loss model, or CPU microarchitecture study. Only the sparse pattern appears on the fast local link.

*Table 1. Fixed DEMO results. Delay columns are median/p95 milliseconds; wire size is median KiB; retention is peak payload MiB; preparation is median milliseconds. Binary units apply. IT completion is diagnostic because its intermediate displays may be incoherent.*

| Changed tiles / link | Method | Coherent runs | Delay med. | Delay p95 | Wire KiB | Payload MiB | Prepare ms |
|---|---|---:|---:|---:|---:|---:|---:|
| 4 / constrained | FS | 120/120 | 87 | 106 | 1026 | 2.00 | 0.18 |
| 4 / constrained | IT | 71/120 | 13 | 26 | 66 | 1.06 | 0.05 |
| 4 / constrained | SP | 120/120 | 17 | 31 | 68 | 1.06 | 0.32 |
| 24 / constrained | FS | 120/120 | 89 | 110 | 1026 | 2.00 | 0.18 |
| 24 / constrained | IT | 40/120 | 47 | 69 | 386 | 1.38 | 0.07 |
| 24 / constrained | SP | 120/120 | 51 | 74 | 388 | 1.38 | 0.37 |
| 60 / constrained | FS | 120/120 | 91 | 111 | 1026 | 2.00 | 0.18 |
| 60 / constrained | IT | 31/120 | 83 | 104 | 962 | 1.94 | 0.09 |
| 60 / constrained | SP | 120/120 | 97 | 120 | 964 | 1.94 | 0.44 |
| 4 / fast local | FS | 120/120 | 2.2 | 3.1 | 1026 | 2.00 | 0.18 |
| 4 / fast local | IT | 71/120 | 1.3 | 2.2 | 66 | 1.06 | 0.05 |
| 4 / fast local | SP | 120/120 | 2.6 | 3.9 | 68 | 1.06 | 0.32 |

FS and SP meet the coherence criterion in all rows. IT does not, despite revision tags, and its lower delays cannot establish a coherence-preserving speed advantage. Against FS, SP reduces constrained-link median completion from 87 to 17 ms with four changed tiles and from 89 to 51 ms with 24. Corresponding wire sizes fall from 1,026 KiB to 68 and 388 KiB. The p95 comparisons also favor SP in these two cases.

With 60 changed tiles, SP still transfers fewer bytes, but median completion rises from 91 to 97 ms and p95 from 111 to 120 ms. Under the fast local link, four changed tiles again save bytes while median completion rises from 2.2 to 2.6 ms. SP preparation is higher in every pair: 0.32–0.44 ms versus FS's 0.18 ms. These observations are consistent with preparation and manifest handling offsetting transfer savings, but do not isolate those components' causal contributions.

Payload retention declines from FS's 2.00 MiB to SP's 1.06, 1.38, and 1.94 MiB as changes become denser. These values exclude pointer tables and descriptors and assume one reader finishes within a measured display cycle. They cannot establish bounded total memory for stalled readers.

## 4. Functional Evidence and Adoption Limits

A separate suite comprises 28 hand-authored traces, all matching SP's target-root oracle. Cases include first connection without a base, empty patches, delayed final tiles, reordered or duplicate packets, conflicting duplicates, corruption, disconnect during staging, late packets after reconnect, base eviction, and two pinned readers. Eight base-eviction/reconnect traces use FS fallback. No recovery-latency summary exists, and fallback cannot inherit the sparse-path byte savings.

Two development variants explain why apparently minor protocol decisions matter. Removing base checking exposes mismatched roots in two of six reconnect traces. Acknowledging the first packet instead of publication fails after coalescing in one of six. Coalescing generates target values once per coordinate, and range checks reject malformed tile IDs. These are functional observations, not timing ablations or an exhaustive correctness proof.

The fixtures therefore favor SP when changes are sparse enough and transport constrained enough to repay its preparation. FS remains a coherent alternative and is faster in the dense and fast-link examples. Choosing between them would require workload evidence beyond these fixed cases; no adaptive selector is evaluated. Allocation-failure injection, process crashes, authentication, security, and Byzantine behavior are outside the implemented coverage. No literature survey or deployment evidence supports a universal novelty or production-readiness claim.

## 5. Conclusion

Base-referenced staging allows changed-tile transfer to preserve an existing renderer's coherent publication behavior. Pinning the acknowledged base, assembling target values privately, and acknowledging publication together make that operation meaningful across interruptions. The synthetic comparisons support conditional transfer and latency benefits, with explicit dense-change and fast-link reversals. They establish an editorial demonstration of a bounded design argument, not measured real-world performance.
