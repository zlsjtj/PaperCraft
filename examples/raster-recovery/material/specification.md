# Constructed system specification

**SYNTHETIC DEMO ONLY.** This is an authored engineering case and executable discrete-event accounting model. There is no real apparatus, measured benchmark, field outage dataset, or external literature evidence. Dimensions and durations are assumptions. Internal source identifiers S1 through S4 refer only to this package.

## Objects and coordinates

- A carriage visits 192 fixed sample centers, arranged as 12 rows by 16 columns.
- Origin is the center at row 0, column 0. x increases with column; y increases with row. x = 4c mm; y = 6r mm. Sample-center extent is 60 mm by 66 mm. No enclosure dimensions are specified.
- Rows are visited r = 0 ... 11. Within a row, traversal index k = 0 ... 15. Physical c = k for even r; c = 15-k for odd r. Logical ordinal q = 16r+k.
- Every sample returns a 256 byte synthetic payload. The model's correctness target is one durable logical result at each ordinal. Acquisition can be repeated without an external side effect; stability of a changing real object is outside this definition.
- On startup or restart, homing costs 120 ms. Every row entry costs 30 ms. After a restart, a known row entry reference and travel to the first missing position are included in this single anchor event. The fixed duration is a simplification, not a distance calculation.

## Persistence policies and behavior

| ID | Volatile payload | Commit unit | Configured commit time | Recovery lookup after a cut |
|---|---:|---|---:|---:|
| RC | 4096 bytes | 16-record row, staged payload plus row checkpoint | 4 ms per row | 1 ms |
| AR | 256 bytes | self-validating 272-byte record | 0.8 ms per record | 4 ms |
| BS | 1024 bytes | 1048-byte sealed block of four records | 2 ms per block, plus 1 ms row checkpoint | 6 ms |

All policies have a 10 ms acquisition event per sample. Events execute serially. There is no overlap, erase model, wear model, cache model, communication delay, or measured latency calibration.

RC's row commit is an abstraction: payload staging precedes publication of the new row descriptor; a cut at any point before the combined event completes does not publish the row. This does not assume that physical memory atomically writes 4096 bytes. Two 64-byte checkpoint slots alternate. The demonstration checkpoint carries a generation number, epoch, next row, and checksum; recovery chooses the valid slot with the largest generation. Initial checkpoint next_row is 0. `model.py` exercises byte checksums on metadata examples, but does not implement a device driver or byte-exact 64-byte slot serializer.

AR publishes each record only after its whole append event completes. Its 16-byte metadata allowance is included in 272 bytes. Recovery obtains the first missing ordinal from a verified contiguous record prefix. Index scans and validity checks are represented by the fixed lookup cost.

BS keeps RC's alternating checkpoint mechanism. A row consists of four ordered block positions b = 0 ... 3. Each block contains traversal positions k = 4b ... 4b+3; block positions follow traversal order, not increasing x. A block has 1024 payload bytes plus a 24-byte seal allowance. The seal represents epoch, row, block index, record count, and payload CRC32 information. A valid seal is published only after the payload is durable. This ordering is assumed by the model and not demonstrated on hardware.

BS recovery starts at the checkpoint's next row. It inspects block 0, then 1, 2, 3. Each candidate must be sealed, match expected epoch/row/index, contain four records, have 1024 payload bytes, and pass payload CRC. Recovery stops at the first invalid or absent block. A later valid block does not bridge a hole. When all four blocks are valid but the row checkpoint has not advanced, recovery finishes the row checkpoint, then enters the next row. A CRC-valid payload is not evidence of a correct physical coordinate.

The simulator represents persistent data by a durable-prefix integer and row-checkpoint integer. The independent seal and slot routines exercise validation on constructed byte arrays. These two levels are related but are not a complete byte-level crash emulator.

## Durations and cuts

`data/parameters.json` is the machine-readable parameter source. Each trace lists absolute times on cumulative powered time. The clock pauses while power is off. The same cut times are used for all policies. A cut exactly at an event's scheduled completion wins: that event is interrupted before publication. Interrupted acquisition does not count as a completed acquisition. Its consumed duration remains in powered time.

Every cut discards volatile state and resumes at the previously durable prefix. Partially staged data and unsealed blocks are not accepted. `events.csv` records the durable prefix before each event; publication updates the prefix after an uninterrupted commit. Completed acquisitions minus 192 is the reported completed-reacquisition count. Off time is 40 ms per encountered cut and appears only in `elapsed_including_off_ms`.

The 12 profiles were constructed as diagnostic examples, not sampled from a real or probabilistic outage process. T0 is uninterrupted; T1 and T2 are two irregular two-cut cases; T3 and T4 have six cuts; T5 has ten cuts. T6 through T11 include the entire regular two-cut probe set with spacings 500, 600, 700, 800, 900, and 1000 ms. No statistical population, probability, average speedup, variance, or confidence interval is justified.

## Figure source facts

The two supplied images are rough original sketches to be redrawn. They are factual starting points, not layout templates. Both originals use 1500 by 1050 pixels. Each final figure has a fixed 160 by 112 mm canvas, including its whitespace; redraws must retain this canvas size.

Figure 1 objects: sampled plane, 12 ordered rows, 16 centers per row, alternating traversal direction, logical four-record blocks, a row entry reference, completed work, durable blocks, volatile work, interrupted work, and the restart point. Figure 1's example is a state illustration independent of trace timing. Rows 0...4 are complete; epoch = 7; checkpoint next_row = 5. In row 5, sealed blocks 0 and 1 cover k 0...7 / c 15...8. Acquisitions k 8 and 9 / c 7 and 6 are volatile. Acquisition k 10 / c 5 is interrupted. Blocks 2 and 3 are unaccepted. First missing q = 88, at r 5, k 8, c 7, x 28 mm, y 30 mm. The entry reference of row 5 is c 15, x 60 mm. The row traverses toward decreasing x. Repeating the two volatile samples is permitted.

Figure 2 objects: logical ordinal generator; current physical coordinate; a volatile four-record buffer; persistent block payload and its seal; two alternating persistent row checkpoint slots; a recovery reader; validation decisions; accepted prefix; home/row-anchor operation; and subsequent acquisition. Forward behavior acquires four samples, writes payload, publishes the block seal, and after four blocks publishes a row checkpoint. Failure discards the volatile buffer. Recovery reads checkpoint and block metadata, chooses only the valid contiguous prefix, then establishes physical position before acquiring again. The accepted-prefix relationship and physical-position relationship are distinct. No direct path from checksum validation to trusted physical position is justified.

## Failure control

The coordinate-control case starts at the Figure 1 state. Inject a fixed +4 mm residual x displacement after reset. Examine the eight remaining samples k = 8 ... 15 of row 5. With the anchor event, actual physical columns equal intended columns 7 ... 0. If the anchor event is omitted, actual physical columns are 8 ... 1 while logical labels remain 7 ... 0. The resulting 8 of 8 incorrect assignments are consequences of a prescribed arithmetic injection, not observed rates of mechanical drift. Row 6 and later are not part of this control.

## Storage accounting

Payload-buffer allowances exclude runtime and metadata RAM. Completed-job persistent allowances exclude alignment, allocators, and filesystems:

- RC: 192*256 + 2*64 = 49280 bytes.
- AR: 192*(256+16) = 52224 bytes.
- BS: 48*(4*256+24) + 2*64 = 50432 bytes.

Byte counts do not determine the chosen write-event costs. An actual implementation would have to measure and justify both.
