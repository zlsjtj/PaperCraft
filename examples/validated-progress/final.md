# Validated Progress Slots Reduce Restart Inspection in a Block Export

*DEMO teaching manuscript. All traces and counts are constructed examples, not production workloads or measured benchmarks. No literature priority is claimed.*

## Abstract

The existing block exporter recovers correctly by scanning its output for the longest valid prefix. Two alternating progress slots let restart check a recorded boundary before resorting to that scan. Progress is recorded after the corresponding output data are synchronized and is validated against the named block at restart. In the constructed clean-finish trace, this changes inspection from 100 data headers to two progress entries and one data header. A torn latest slot causes one block to be replayed in another trace; invalidity of both slots restores the full scan. The shortcut costs one additional progress-slot synchronization per block. These teaching examples expose a tradeoff between recording durable progress and inspecting output, without measuring total restart time or export efficiency.

## 1. Introduction

The existing export already has a correct recovery path: read its sequential output, check blocks in order, and stop at the first invalid block. This finds the longest valid prefix from which processing can resume. Its cost is repeated inspection of the output, including the constructed clean-finish case in which all 100 blocks are already durable. The question in this exercise is therefore whether recovery can locate a usable prefix with less inspection while retaining the scanner as a fallback.

A saved byte offset seems to offer that shortcut, but it matters when the offset is saved. The simple comparator records the end of a write as soon as the write returns. In the stated storage model, those bytes may still disappear or be torn on power loss. Resuming after that offset can skip records whose output never became durable. The offset avoids work by trusting a boundary that the crash model does not justify.

The proposed procedure instead records completed progress after synchronizing the corresponding output data. It alternates between two checksummed slots and validates a candidate entry against its named block before using it. The four supplied traces examine clean completion, nondurable data, a torn latest slot, and invalidity of both slots. Together they show what this concrete addition changes relative to the existing code baseline and where its advantage disappears. Generation numbers and checksum slots are common techniques; no prior-art search establishes a new recovery algorithm.

## 2. Method

The exporter writes a local output file in fixed input order, using 512 records per block. The existing format contains a length, sequence number, payload, and checksum. Its unchanged scanner finds the longest valid prefix and stops at the first invalid block. Checksums detect the corruption considered in this teaching model, rather than arbitrary adversarial collisions.

For each block, the exporter appends the block and synchronizes the output data. It then writes the alternate progress slot with a generation number, the last completed block number, the block's end offset, and its digest. Each progress entry also has its own checksum. After synchronizing the progress slot, the exporter acknowledges that generation. Thus acknowledgment follows both the data synchronization and the separate synchronization of the progress record. The finished flag follows the same ordering after the final data.

Restart checks both progress slots. An entry is usable only if its own checks pass and its named data block validates; recovery selects the largest generation among usable entries and resumes after that completed prefix. If neither entry validates, restart runs the original full-prefix scanner. The two slots occupy disjoint fixed locations, so a torn write to the latest slot need not invalidate the previous one. Nevertheless, the design does not prove protection against losing both slots.

Choosing the preceding generation can require replay of data that was already valid. In trace C3, block 100 is durable but the latest slot is torn; the previous valid entry names block 99. Recovery therefore rewrites block 100 from the selected prefix rather than appending a duplicate. Replay requires the input to remain available and deterministic.

The ordering relies on the storage model: data acknowledged by a successful data synchronization survives the modeled power loss. Before synchronization, a completed write may be absent or torn after restart; progress-slot writes may also tear. Devices that falsely report completed flushes are outside this guarantee. The procedure adds one progress-slot synchronization per block, whereas the old scanner has no side-progress synchronization cost. That added work may dominate on some storage.

## 3. Results

Table 1 preserves all supplied traces. Data-header counts and progress-entry reads are separate units of inspection; replay counts describe blocks rewritten after the selected prefix. No wall-clock latency is attached to these counts.

*Table 1. Constructed restart operations and the offset-only comparator's failure condition.*

| Trace and condition | Full-scan headers | Progress-entry reads | New data headers | New replayed blocks | Full-scan fallback | Offset-only skips unwritten output |
|---|---:|---:|---:|---:|---|---|
| C1: clean finish, 100 durable blocks | 100 | 2 | 1 | 0 | No | No |
| C2: block 100 written but not durable; progress at 99 | 100 | 2 | 1 | 1 | No | Yes |
| C3: block 100 durable; latest slot torn; previous valid at 99 | 100 | 2 | 1 | 1 | No | No |
| C4: both slots invalid; 100 durable blocks | 100 | 2 | 100 | 0 | Yes | No |

After the clean finish in C1, the new procedure substitutes two progress-entry reads and one named data-header inspection for the 100-header scan, with no replay. C2 and C3 retain that inspection count but each replay one block. These are the supplied trace counts, not measurements of elapsed recovery time.

The identical replay counts in C2 and C3 distinguish two recovery decisions. In C2, replay restores block 100 because a returned write did not make it durable. In C3, replay conservatively rewrites a durable block because recovery can validate only the older recorded boundary. The offset-only comparator skips unwritten output in C2, so its apparent avoidance of work is a recovery failure. The safe full scanner, rather than that shortcut, is the relevant baseline for judging inspection cost.

C4 removes the inspection saving. With both slots invalid, the new procedure reads the two entries and then inspects all 100 data headers using the unchanged scanner. All 100 blocks are durable, so it replays none. The fallback preserves the existing recovery path; it does not provide a shortcut in this case.

## 4. Discussion

The addition changes how restart discovers completed progress. When a usable slot exists in the supplied traces, recovery can inspect a recorded boundary instead of rediscovering the prefix through the complete scan. This benefit depends on recording progress after durable data and verifying the record on restart. The offset-only shortcut illustrates why a smaller operation count is insufficient when the selected boundary can skip missing output.

The old scanner remains a meaningful alternative. It already handles the modeled crashes correctly and avoids the per-block side-progress synchronization. The new design pays that synchronization during export to reduce later inspection, and can still pay for the full scan if both entries are invalid. The traces therefore motivate a tradeoff between writing progress and inspecting output, rather than establish that the new design is always preferable.

The fallback and replay cases also limit what the extra metadata buys. A preceding slot can remain usable when the latest one tears, but it may identify an older prefix than the valid output would permit. That conservatism requires deterministic input to be available for rewriting. When neither slot validates, the metadata provides no inspection shortcut at all. The four traces do not establish a general replay bound or a failure probability.

No storage latency, wall time, energy, flash wear, or throughput was measured, and replay is only part of restart cost. The data cannot rank total recovery time or net export efficiency. They support a narrower teaching conclusion: validated progress can reduce restart inspection while retaining an existing safe scanner, at an explicit synchronization cost and with replay and fallback cases that must remain visible.
