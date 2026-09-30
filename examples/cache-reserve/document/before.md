# Preparing Free Space Within a Fixed CLOCK Scan Budget: A Fictional DEMO

**FICTIONAL DEMO — specification and authored illustrative values only. No implementation, trace replay, simulation, physical experiment, production deployment, or statistical trial was performed.**

## Abstract

A variable-size object cache may inspect many small objects before finding enough space for one large insertion. Capping this search bounds reference examinations but can reject a fetched object that would otherwise become resident. We specify a CLOCK variant that spends part of the same request budget preparing free space after each request. Its 48 foreground and 16 maintenance examinations preserve a 64-examination limit while pursuing a soft free-space target. An authored MixedBurst fixture assigns the 8 MiB variant 67.00% request hits versus 63.50% for a simple 64-examination cap, with mean examinations increasing from 12 to 14. SteadySmall instead assigns fewer hits and more examinations to the reserve variant. These fictional values illustrate the trade between preparing space and retaining reusable payloads; they establish no performance gain. The exercise specifies how tentative foreground eviction and immediate maintenance eviction share one budget, and why request hits, fetched bytes, and average examinations must be judged together.

## 1. Space needed now or prepared earlier

Consider an image-service cache holding immutable objects of different sizes. Its circular list gives referenced objects a second chance: a hit sets a bit, and a scanner clears set bits before selecting objects with clear bits for eviction. A large insertion may require many small victims; a mostly referenced list can require further examinations before any bytes become available. Lookup alone therefore does not determine reclamation work.

The local policy Cap64 stops after 64 examinations. This already provides the examination bound sought here. The question for a reserve policy is whether using some of that allowance to release space before a later miss could justify fewer retained objects and maintenance on hits. Reserve8 changes when reclamation occurs, rather than tightening Cap64's limit. We describe that change and its necessary accounting, then use fixed DEMO rows to expose the competing outcomes without claiming that they occurred in an executable cache.

Figure 1. Allocation of the reference-examination allowance. Bar length represents the specified maximum, not elapsed time or observed work. The reserve variants use separate limits of 48 foreground and 16 maintenance examinations; maintenance seeks a soft free-space target and may stop earlier or leave it unmet.

## 2. A request budget shared with maintenance

All five local policies have the same 64 MiB payload capacity, C. Requests are serial; keys, sizes, and payloads are immutable, with no expiration, deletes, failures, or concurrent requests. The cache starts empty. Its index, temporary victim pointers, response buffers, and allocator overhead are outside C, so this is not a server-memory bound. Crash recovery, cancellation, and tenant isolation are unspecified.

On a miss, the service fetches and returns the payload even if insertion is rejected. If free bytes suffice, it inserts immediately. Otherwise, the foreground scan examines the object at the hand, advances the hand, clears referenced bits, and records unreferenced objects as tentative victims. It commits their removal only when free bytes plus selected bytes cover the incoming payload. An exhausted allowance discards the victim list while retaining bit clears and hand movement. Thus, foreground failure does not discard resident payloads merely because an incomplete scan selected them.

Revisiting a tentative victim counts as another examination but must not count its bytes again. Otherwise, repeatedly encountering one object could appear to supply space that does not exist. Committing removals also moves a removed hand to a surviving object; an empty ring uses a null hand. New objects enter immediately before the hand with bit 1. These rules specify the bookkeeping required for correct admission, not completed engineering validation. The payload counter must remain between zero and C after committed operations; aggregate results cannot verify that invariant.

CLOCK continues scanning until enough space is found. Under the stated serial assumptions, clearing bits eventually exposes sufficient victims for any object fitting C. Cap64 allows at most 64 foreground examinations. Reserve4, Reserve8, and Reserve16 instead allow 48, followed by at most 16 maintenance examinations targeting 4, 8, and 16 MiB of free space, respectively.

Maintenance runs after every request's lookup and admission decisions, including hits and bypasses. While below the target, it clears referenced bits or immediately evicts unreferenced objects, stopping at the target, an empty ring, or its allowance. There is no detached worker or uncharged catch-up pass. The last eviction may overshoot the target; the allowance may expire before reaching it. A foreground insertion may consume all available space, so the reserve neither guarantees admission nor imposes a hard minimum of free bytes.

Maintenance may remove the object just served or inserted. Separate response ownership makes that permissible in this serial specification, although it can harm reuse. Both scanning phases count toward the reserve policies' maximum of 48 + 16 = 64 examinations per request. Hashing, membership checks, unlinking, hit-bit writes, allocation, copying, and origin service remain outside this metric. A bounded victim-pointer array does not turn that examination bound into a CPU-work or response-time guarantee. Objects larger than C bypass immediately; the fixture contains none.

## 3. What existing admission mechanisms establish

TinyLFU compares approximate recent frequencies of an incoming item and an eviction candidate [1](https://arxiv.org/pdf/1512.00727). S3-FIFO uses a small FIFO queue to filter low-reuse objects before the main queue; its ghost queue stores identities without payloads [2](https://www.cs.cmu.edu/~rvinayak/papers/s3-fifo-sosp-2023-fifo-queues-are-all-you-need-for-cache-eviction.pdf). AdaptSize adjusts probabilistic size-aware admission using a Markov model for a CDN hot-object cache whose objective emphasizes object hits [3](https://www.usenix.org/system/files/conference/nsdi17/nsdi17-berger.pdf).

These works establish relevant admission and filtering ideas, not results for our local policies. A payload-free reserve is not S3-FIFO's small queue, and avoiding origin bytes is not the same objective as maximizing request hits. None of these systems was implemented here. The limited source search cannot establish originality, closest-work ranking, or priority for reserves, bounded CLOCK scans, or eviction scheduling.

## 4. Reading the constructed comparisons

Table 1 gives all 20 DEMO rows: five policies in four scenarios, each assigning 1,000,000 requests including cold start. Payloads are 4 KiB, 64 KiB, or 1 MiB. SteadySmall describes stable small-object reuse; MixedBurst introduces large-object bursts; HotShift changes popular keys; LargeReuse emphasizes repeated large payloads. These descriptions are not trace-generation recipes. Size-class counts and all examination, bypass, and maximum values were manually assigned. No request ordering is supplied, and identical sequences across policies cannot be certified.

Request-hit ratio is hits divided by requests. Origin bytes sum each size-class miss count times its payload size; integer bytes are authoritative, and MiB uses 2^20 bytes. Mean examinations include foreground and maintenance work. A budget bypass is a miss rejected when foreground allowance expires; its full payload is still fetched. Repetitions are zero, so there are no confidence intervals, latency samples, or statistical significance claims.

*Table 1. FICTIONAL DEMO outcomes at a common 64 MiB payload capacity. Within each scenario, compare CLOCK with Cap64 for the simple cap, Cap64 with Reserve8 for the shared-budget design, and all three reserve targets for sensitivity. Maxima are authored examination counts, not latency percentiles.*

| Scenario | Policy | Hits (%) | Fetched (MiB) | Bypasses | Mean exams | Max exams |
| --- | --- | --- | --- | --- | --- | --- |
| SteadySmall | CLOCK | 92.50 | 11718.7500 | 0 | 0.85 | 2048 |
| SteadySmall | Cap64 | 92.25 | 12285.1562 | 2500 | 0.82 | 64 |
| SteadySmall | Reserve4 | 91.45 | 12550.7812 | 500 | 1.40 | 64 |
| SteadySmall | Reserve8 | 90.10 | 13453.1250 | 250 | 1.80 | 64 |
| SteadySmall | Reserve16 | 86.80 | 15398.4375 | 120 | 2.40 | 64 |
| MixedBurst | CLOCK | 63.00 | 87578.1250 | 0 | 15.00 | 8192 |
| MixedBurst | Cap64 | 63.50 | 97226.5625 | 12000 | 12.00 | 64 |
| MixedBurst | Reserve4 | 65.20 | 89835.9375 | 7000 | 13.00 | 64 |
| MixedBurst | Reserve8 | 67.00 | 81562.5000 | 4000 | 14.00 | 64 |
| MixedBurst | Reserve16 | 66.20 | 76789.0625 | 2000 | 17.00 | 64 |
| HotShift | CLOCK | 59.50 | 95625.0000 | 0 | 12.00 | 6144 |
| HotShift | Cap64 | 58.50 | 100761.7188 | 16000 | 10.00 | 64 |
| HotShift | Reserve4 | 59.50 | 95566.4062 | 10000 | 10.50 | 64 |
| HotShift | Reserve8 | 60.60 | 90250.0000 | 6000 | 12.00 | 64 |
| HotShift | Reserve16 | 59.30 | 86667.9688 | 3000 | 14.00 | 64 |
| LargeReuse | CLOCK | 82.00 | 74531.2500 | 0 | 3.00 | 4096 |
| LargeReuse | Cap64 | 80.20 | 94582.0312 | 20000 | 2.70 | 64 |
| LargeReuse | Reserve4 | 80.30 | 92585.9375 | 16000 | 3.20 | 64 |
| LargeReuse | Reserve8 | 79.80 | 89851.5625 | 14000 | 4.00 | 64 |
| LargeReuse | Reserve16 | 78.50 | 80527.3438 | 7000 | 5.50 | 64 |

MixedBurst illustrates why the maximum alone cannot select a reserve. CLOCK's assigned maximum is 8,192; Cap64 and Reserve8 both have 64. Relative to Cap64, Reserve8 has 635,000 → 670,000 hits, 97,226.5625 → 81,562.5000 MiB fetched, and 12,000 → 4,000 budget bypasses. Its total examinations increase from 12 million to 14 million. The fixture couples a more favorable hit/byte outcome with additional average scanning. Cap64 and Reserve8 also differ in foreground allowance, 64 versus 48. Their comparison concerns the complete budget split and reserve policy; it cannot isolate the effect of maintenance or identify the cause of the assigned values.

SteadySmall reverses that apparent benefit: Cap64 → Reserve8 changes request hits from 92.25% to 90.10%, mean examinations from 0.82 to 1.80, and origin fetches from 12,285.1562 to 13,453.1250 MiB. HotShift assigns 58.50% → 60.60% hits, but mean examinations also rise from 10 to 12. LargeReuse separates the objectives: hits fall from 80.20% to 79.80% while origin fetches fall from 94,582.0312 to 89,851.5625 MiB and mean examinations rise from 2.70 to 4.00.

Nor does increasing the reserve identify one winner. MixedBurst assigns Reserve4/8/16 hit ratios of 65.20%/67.00%/66.20%, yet Reserve16 fetches the fewest bytes of those three. SteadySmall assigns 91.45%/90.10%/86.80% hits as the target grows. These authored tensions illustrate that reserving space can displace reusable payloads; they do not establish a causal explanation or an optimal target.

## 5. Scope and conclusion

The specification moves some reclamation ahead of future misses while charging it to the current request's fixed allowance. Cap64 remains the simpler sufficient choice for the examination bound alone. Whether preparation is useful requires an implementation, realizable traces, and published-policy comparisons under an explicit objective. The present work provides neither throughput nor deployment-cost evidence and cannot reproduce cache-state evolution. Its concrete outcome is a bounded-scan design and an inspectable fictional comparison that makes the cost of spare capacity part of the decision.

## References

[1] Gil Einziger, Roy Friedman, and Ben Manes. *TinyLFU: A Highly Efficient Cache Admission Policy*. arXiv:1512.00727. [Author-uploaded paper](https://arxiv.org/pdf/1512.00727). Source S1 in `sources.md`.

[2] Juncheng Yang, Yazhuo Zhang, Ziyue Qiu, Yao Yue, and K. V. Rashmi. *FIFO Queues are All You Need for Cache Eviction*. SOSP 2023. DOI: 10.1145/3600006.3613147. [Author-hosted paper](https://www.cs.cmu.edu/~rvinayak/papers/s3-fifo-sosp-2023-fifo-queues-are-all-you-need-for-cache-eviction.pdf). Source S2 in `sources.md`.

[3] Daniel S. Berger, Ramesh K. Sitaraman, and Mor Harchol-Balter. *AdaptSize: Orchestrating the Hot Object Memory Cache in a Content Delivery Network*. NSDI 2017, pp. 483–498. [Conference paper](https://www.usenix.org/system/files/conference/nsdi17/nsdi17-berger.pdf). Source S3 in `sources.md`.
