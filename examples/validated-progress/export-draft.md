# Block export with checks and recovery

DEMO. This is an original teaching manuscript. All traces and counts below are constructed examples, not production workloads or benchmarks. No literature priority is asserted.

Our export program processes records in blocks. Each block has a sequence number and a checksum. The process writes a block and updates a progress file. The previous implementation scans the checksum chain on restart and reprocesses a suffix. We implemented two progress slots, generation numbers, a block digest, a checksum on the progress entry, and validation at restart. There are 512 records per block. The implementation also has a flag indicating that an export is finished. The slots alternate. We used fault traces and counted replayed blocks. These features improve the export system.

The application writes to a local output file. It can restart after interruption. The existing output scan is correct for the modeled crash behavior. A separate simple optimization records the byte offset of the most recent write, without checking whether those bytes are durable. The new version records a completed generation after the required data synchronization. The progress entry is small. Replay is only part of restart cost. We did not measure storage latency.

On a 100-block constructed export, the prior full scan inspects 100 block headers after a clean finish. The new method reads two progress entries and validates one named data block. Several traces also include incomplete writes, damage to a progress slot, and both slots being invalid. The unsafe write-offset optimization appears to do less work in one trace. The new version contains a fallback. Results and the source note should be considered together.

Please improve the title, abstract, and connected introduction/method/results/discussion in English. Preserve all supported facts and limitations. Do not add experiments or pretend these are measured research results. There is no required number of contributions.
