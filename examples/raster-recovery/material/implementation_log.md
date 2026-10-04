# Local construction record

All entries describe construction of this synthetic DEMO package. Step identifiers are a development sequence, not invented dates or laboratory receipts.

| Step | Change made | Artifact and limitation |
|---|---|---|
| E01 | Defined the 12 by 16 serpentine grid, ordinal mapping, and 256-byte payload. | `model.py` coordinate functions. Coordinates are invented, not surveyed. |
| E02 | Built the RC scaffold with a row buffer, staged row commit, and alternating checkpoint slots. | RC accounts for 4 ms at each completed row; slot reader is separately tested on constructed metadata. |
| E03 | Retained the RC checkpoint reader and slot selection rule for reuse. | Generation and checksum reject a torn newer checkpoint. No storage-driver implementation is supplied. |
| E04 | Added AR with a durable record after every acquisition. | Uses 0.8 ms per commit and 256 bytes of payload buffering. The same movement and outage model applies. |
| E05 | Added BS buffers, block seals, ordered prefix validation, and row checkpoint completion after a fully sealed row. | Four samples per block; RC slot protocol remains. Payload-before-seal durability is a model assumption. |
| E06 | Explicitly charged homing and row anchoring after reset. | Home does not reveal which logical records survived. Prefix recovery does not establish physical position. |
| E07 | Added the +4 mm coordinate displacement injection with and without anchoring. | Deterministic arithmetic control, restricted to eight remaining samples in row 5. |
| E08 | Added named checks, the 384-case finite single-cut sweep, and per-event ledgers. | Checks are local model executions. No physical runtime, empirical error probability, endurance, or power data was produced. |
| E09 | Retained all twelve trace profiles, including the full six-spacing regular two-cut probe set. | No real outage distribution is claimed and no pooled statistical summary is provided. |

The source manuscript was written from these internal materials. It intentionally has uneven ordering and repeated details. Internal source tags denote inspectable package files; there are no fabricated external citations. Neither the construction log nor the manuscript establishes scientific novelty against outside work.
