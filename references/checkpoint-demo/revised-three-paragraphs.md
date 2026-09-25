# 英文修订示例

以下三段对应合成教学输入，不是真实科研结果。

We introduce a checkpoint staging path that overlaps compression of independent chunks with writes of earlier chunks. The serial baseline waits for compression before each write; both paths use the same compressor and grouped writes. The incremental change is the overlap between these stages. The queue holds at most four chunks, a choice based on available memory; no queue-size sensitivity study was performed.

Cancellation and restart can leave a late result targeting a recycled buffer. Admission therefore requires both the chunk ID and checkpoint generation to match the current slot, and the content checksum is checked before committing a chunk. Buffers are released only after the writer completes or cancellation invalidates ownership. Directed fault injections of stale generations, wrong chunk IDs and checksum mismatches were rejected. Completed-write counts measure activity. No exhaustive proof, power-loss test or crash-recovery experiment was performed.

At one fixed thread count, median elapsed times over five repeated runs per input were 10.0/9.0 s, 20.0/19.0 s and 1.0/1.1 s for the serial baseline/forced staging paths on A, B and C, respectively, excluding file creation and cleanup. For identical work per input, these correspond to throughput changes of +11.11%, +5.26% and −9.09%. Thus, forced staging helped A and B but slowed C. The selected configuration uses staging above 64 MiB and retains the original serial path for smaller checkpoints. This threshold was selected after preliminary timings on the same three inputs, without an independent tuning/test split; the forced-path comparison does not independently validate the selected policy or its generality.
