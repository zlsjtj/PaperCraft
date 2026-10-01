> **DEMO disclosure:** These original synthetic editorial-evaluation materials do not report real experiments. All numerical results below are authored fixtures.

# Coherent Sparse Raster Updates from Named Revision Bases

## Abstract

Incrementally transferring a raster can reduce communication while exposing combinations of tiles that never belonged to a producer revision. We examine a staged-patch protocol for an existing renderer that already uses immutable tile versions and atomic root publication. The protocol names a base and target revision, stages changed tiles privately, and publishes only a validated target root. Its contribution within this demonstration is the coordination of sparse transfer with an existing coherent-view contract, including acknowledgement, coalescing, and fallback rules. Authored fixtures compare staged patches with staged full snapshots and immediate tile installation. On the constrained-link sparse case, staged patches preserve coherence in all 120 prescribed runs while reducing median wire volume from 1026 to 68 KiB and completion delay from 87 to 17 ms relative to full snapshots. Dense changes and a fast local link reverse the latency advantage. These fixtures illustrate a conditional tradeoff; they establish neither empirical performance nor research novelty.

## 1. Introduction

A raster dashboard should display a complete producer revision while new values travel over a connection that can delay or reorder messages. The values themselves are assumed already computed. Sending only changed tiles appears attractive when successive maps share most of their content, but completing individual transfers is not enough: the renderer can observe an old tile beside a new tile before the update finishes.

The application studied here already addresses local consistency. A frame captures one published root, which points to immutable tile versions. Atomic root publication, reference counting, root copying, checksums, and sparse invalidation all predate the transfer changes. The question is how to preserve that rendering contract across incremental network delivery.

The resulting staged-patch design combines a named revision base with private assembly and publication after validation. Full snapshots supply the coherent comparison; immediate installation reveals the consequence of omitting staging. The necessary work lies in handling revision history and interrupted delivery consistently, rather than in introducing a new atomic-swap primitive. Our evidence consists entirely of synthetic fixtures and hand-authored functional traces. It supports an inspectable design argument and identifies circumstances where sparse transfer ceases to help.

## 2. Protocol and implementation

### 2.1. A target root, not uniformly new tiles

Each root contains 64 tile-version pointers. A tile has 4096 four-byte cells, yielding a full raster payload of 1,048,576 bytes. A coherent target view matches the producer's target root. It may include unchanged tiles created several revisions earlier; coherence does not require every tile to carry the same creation timestamp.

We compare three implementation strategies. Full snapshots (FS) stage an entire raster, validate every packet, and switch the visible root. Immediate tiles (IT) carry target revision tags but install changed pointers as messages arrive. Staged patches (SP) name a base revision, a target revision, and the complete changed-tile set. The client pins its visible base, assembles replacements in a private pending root, and shares unchanged versions from that base. Both FS and SP use the renderer's existing publication operation.

For example, let revision 10 contain tiles (a0, b0), while revision 11 requires (a1, b1). If a1 arrives before b1, IT exposes (a1, b0), which matches neither revision. SP keeps (a0, b0) visible until both replacements validate, then publishes (a1, b1). An unchanged third tile remains shared. This example explains the intended check without adding a timing result. Readers continue using a published root while packets are pending; remote clients need not show the same revision simultaneously.

### 2.2. Revision progress and failure handling

The client acknowledges only a root it has published. The server derives patches from that acknowledged revision when its retained history permits, keeping manifests for at most eight completed revisions in this configuration. To combine several updates, it unions touched coordinates and sends each coordinate's value from the target root. Sending the earliest encountered intermediate value would not reconstruct the target. A coordinate that changes and later returns to its original bytes can remain in the union, so this mechanism is not a minimal-difference compressor.

An unavailable, wrong, or unverifiable base requests FS fallback. Before publication, the pending update is checked against its pinned base. Reordered packets can be staged under their named target; matching duplicates are idempotent, whereas conflicting duplicates reject the patch. Incomplete or invalid pending updates are discarded while the last coherent view remains visible. Size, checksum, and tile-ID checks protect assembly from malformed input. Disconnect discards uncommitted staging, and late valid messages must not modify a newer published root.

These rules connect transport progress to visible state. An acknowledgement on receipt would describe progress the renderer has not committed, potentially giving later coalescing the wrong base. The design concerns volatile display state, not durable transactions or crash recovery.

### 2.3. Resource costs

SP retains old tiles and replacements until readers release their old root; FS similarly retains the old frame and a complete replacement. Each pending update additionally needs a 512-byte root pointer table and 4096 bytes of descriptors and reference counters. Dense patches can require a full frame of pending payload. Old-reader pinning has no proven lifetime bound, and manifest validation and root assembly add preparation cost.

## 3. Evaluation with fixed synthetic fixtures

The table contains all supplied fixture rows. Each uses the same 120 targets, lossless values, and packet schedule within a workload/link pair. Queue capacity is fixed at 32 packets and the retry deadline at 20 ms. An older 64-packet exploratory run is excluded. Serialization and transport are shared except for required payload selection and manifest handling.

Completion measures the interval from producer target publication until all required target packets are applied or staged; it is not first-byte delay. “Coherent” counts runs with no non-target mixed root at any prescribed reader interleaving from request through completion. Old coherent roots remain acceptable while delivery proceeds. This finite check does not cover every possible schedule. IT completion remains diagnostically useful, but its incoherent intermediate views prevent treating it as a valid coherence-preserving performance baseline.

| Workload / link | Method | Coherent / 120 | Median / p95 completion (ms) | Wire (KiB) | Retained payload (MiB) | Preparation (ms) |
|---|---|---:|---:|---:|---:|---:|
| 4 tiles / constrained | FS | 120 | 87 / 106 | 1026 | 2.00 | 0.18 |
| 4 tiles / constrained | IT | 71 | 13 / 26 | 66 | 1.06 | 0.05 |
| 4 tiles / constrained | SP | 120 | 17 / 31 | 68 | 1.06 | 0.32 |
| 24 tiles / constrained | FS | 120 | 89 / 110 | 1026 | 2.00 | 0.18 |
| 24 tiles / constrained | IT | 40 | 47 / 69 | 386 | 1.38 | 0.07 |
| 24 tiles / constrained | SP | 120 | 51 / 74 | 388 | 1.38 | 0.37 |
| 60 tiles / constrained | FS | 120 | 91 / 111 | 1026 | 2.00 | 0.18 |
| 60 tiles / constrained | IT | 31 | 83 / 104 | 962 | 1.94 | 0.09 |
| 60 tiles / constrained | SP | 120 | 97 / 120 | 964 | 1.94 | 0.44 |
| 4 tiles / fast local | FS | 120 | 2.2 / 3.1 | 1026 | 2.00 | 0.18 |
| 4 tiles / fast local | IT | 71 | 1.3 / 2.2 | 66 | 1.06 | 0.05 |
| 4 tiles / fast local | SP | 120 | 2.6 / 3.9 | 68 | 1.06 | 0.32 |

Wire volume and preparation are medians; retained payload is a peak. KiB and MiB are binary units. Wire volume includes framing; retained payload excludes the pointer table and descriptors.

FS and SP pass the coherence criterion in every row. IT passes only 71, 40, and 31 of 120 constrained-link runs as changes increase. Its low delays therefore accompany a different visible-state guarantee.

Against FS, SP reduces sparse constrained-link wire volume by 93.4% and median completion by 80.5%. The 24-tile case also benefits, with 388 versus 1026 KiB and 51 versus 89 ms. At 60 tiles, SP still sends fewer bytes, but completion worsens to 97 versus 91 ms; p95 worsens to 120 versus 111 ms. On the fast local sparse fixture, SP likewise loses at both median and p95. Its higher preparation cost is consistent with additional assembly work, but the fixtures do not isolate latency causes or justify attributing every difference to bytes.

A separate suite contains 28 hand-authored protocol traces, all matching SP's target-root oracle. Cases include initial connection, empty patches, delayed final tiles, reordering, duplicates and conflicts, corruption, disconnect during staging, late reconnect packets, base eviction, and two pinned readers. Eight eviction/reconnect traces use FS fallback; no recovery timing summary exists.

Development failures clarify two rules: removing base checks exposes mismatched roots in two of six reconnect traces, and acknowledging the first packet fails after coalescing in one of six. These are functional failures, not timing ablations.

## 4. Discussion and conclusion

The fixtures show why sparse transfer and coherent publication must be evaluated together. FS already provides coherence, so SP's relevant advantage is conditional communication and completion savings while retaining that contract. IT diagnoses a correctness gap that revision tags alone do not close.

The retained-payload figures assume one reader releases its root within one display cycle; they cannot bound memory for stalled readers. Only sparse changes were included on the fast local link. Each case has one fixed schedule, without repetitions, confidence intervals, stochastic loss modeling, or a CPU microarchitecture study. Allocation-failure injection and process-crash tests are absent; security, authentication, and Byzantine behavior lie outside scope. Fallback costs cannot inherit sparse-path savings.

No supplied literature survey establishes novelty, and there is no deployment evidence. The defensible outcome is a specific integration of acknowledged bases, target-value coalescing, and validated publication over an existing immutable-root renderer. It illustrates when sparse updates can preserve coherent views and where full snapshots remain competitive.
