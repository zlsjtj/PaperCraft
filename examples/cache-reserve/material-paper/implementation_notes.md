# Hypothetical implementation notes — FICTIONAL DEMO

Specification only. No source implementation, executable, trace simulator,
benchmark run, or engineering validation exists in this package.

## Shared state and scope

- Payload capacity C = 64 * 2^20 bytes. All five policies use exactly this C.
- One circular list of resident objects, a valid hand, an index, and an exact
  integer `used_payload_bytes` counter. Each object has one reference bit.
- Serial requests, immutable keys and sizes, no TTL, no deletes, no concurrent
  requests, no failures. The returned payload remains valid independently of
  later eviction; a response buffer is outside C.
- The three fixture sizes are 4 * 2^10, 64 * 2^10, and 2^20 bytes.
- Objects larger than C bypass immediately. None appears in the fixture.
- Index memory, references, temporary victim pointers, response buffers, and
  allocation overhead are excluded. C is not a total resident-set-size bound.
- Empty initial cache; all request counts include cold start. A new object has
  reference bit 1 and is inserted immediately before the hand, so it is at the
  end of the current scan cycle. Inserting into an empty ring initializes hand.

## Foreground procedure

On a hit, return the cached payload and set its reference bit to 1. On a miss,
fetch the payload. If free bytes already suffice, insert without scanning.
Otherwise inspect the object at the hand and advance the hand. A set reference
bit is cleared. A clear reference bit makes the object a tentative victim.
Each examination counts, including revisits. Never add a tentative victim's
bytes twice; when revisited, it contributes no additional freeable bytes.
Continue until `free_bytes + selected_bytes >= candidate_bytes` or the allowance
expires. If enough bytes have been selected, unlink the victims, decrement
used bytes by their exact sizes, then insert and charge the new object. If not,
discard the victim list and bypass insertion. Bit clears and hand movement are
retained on this failed admission; no selected resident payload is removed.

If a selected victim is the current hand when committed, move the hand to the
next surviving object; an empty ring uses a null hand. Selection storage has at
most as many distinct pointers as examinations. A bounded temporary pointer
array suffices for the capped variants; it needs membership checking, whose
CPU cost is not included in the reference-examination counter.

## Five local policy IDs

| CSV policy | Foreground allowance | Post-request allowance | Free-byte target |
|---|---:|---:|---:|
| CLOCK | uncapped | 0 | 0 |
| Cap64 | 64 | 0 | 0 |
| Reserve4 | 48 | 16 | 4 MiB |
| Reserve8 | 48 | 16 | 8 MiB |
| Reserve16 | 48 | 16 | 16 MiB |

All use the foreground procedure above. CLOCK terminates in this serial model
because bits can be cleared, every object fits C, and selected victims do not
lose eligibility while a scan is in progress. There is no external guarantee
about time spent in allocation or fetching.

## Maintenance for the reserve variants

After every request has completed its lookup/admission decisions, perform at
most 16 examinations while free bytes are below the target. For a referenced
object, clear its bit and advance. For an unreferenced object, advance, unlink
it immediately, and release its payload bytes. Stop if the ring is empty or the
target is reached. These evictions are intentional maintenance and are not
rolled back. The target may be exceeded by the size of the last removed object.
If the allowance ends first, leave the target unmet. Foreground free-space use
is never forbidden merely to preserve the target.

Maintenance may evict the object just served or just inserted. Serial execution
and separate response ownership make that safe in this specification, but it
can hurt reuse. There is no background thread and no uncharged catch-up pass.

## Counters and limits

An examination is one inspection of a resident reference bit by either scanner.
Maximum 48 + 16 = 64 for each reserve request; maximum 64 for Cap64. Victim
unlinking, hashing, membership checks, hit-bit writes, fetch work, and byte
copies are outside this metric. It must not be described as all CPU work.

A budget bypass counts a miss rejected because the foreground allowance ended
before enough bytes were selected. Every such miss fetches its full payload
from the origin. Other misses can be admitted or bypassed for other reasons,
but this fixture contains no oversize objects or other rejection conditions.

Exact payload accounting requires `0 <= used_payload_bytes <= C` after each
committed operation. The design gives no hard lower bound on free bytes and no
guarantee of successful admission. The table's aggregate counts do not verify
these state invariants; executable traces would be needed for that.
