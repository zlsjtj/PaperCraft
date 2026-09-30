# Working draft

FICTIONAL DEMO MANUSCRIPT. This text describes a hypothetical design. All numbers
are fixed illustrative fixtures, not measurements. No prototype or experiment
has been executed. Bracketed source identifiers refer to published work; the
DEMO results do not come from those papers.

We consider an in-memory object cache in front of an image service. Requests ask
for immutable objects whose payloads have different sizes. The cache has a
payload limit, and its control path follows a circular list with a reference bit
on each resident object. A hit sets the bit. When an insertion needs space, a
scanner clears set bits and selects objects with clear bits. The immediate
problem in this design note is that finding enough bytes may involve many small
objects. A large insertion and a mostly referenced list can make the amount of
scanning uneven even when the lookup procedure is unchanged.

The proposed service is single-threaded and completes one request before
starting another. Objects have no expiration and the backend never changes a
payload associated with a key. Fetch buffers, the index, and allocator overhead
are outside the payload budget. These exclusions make the specification smaller
but prevent interpreting the budget as the memory consumption of a server. We
have not designed crash recovery, cancellation, concurrent requests, or tenant
isolation. A cache rejection still returns the fetched object to the requester;
it only prevents that object from becoming resident.

Several existing mechanisms are relevant. TinyLFU compares approximate recent
frequencies when deciding whether a candidate should displace a resident item
[S1]. S3-FIFO uses small, main, and ghost FIFO queues, with the small queue
filtering objects before they occupy the main queue [S2]. AdaptSize adjusts
size-aware probabilistic admission for a CDN hot-object cache with an object-hit
ratio objective [S3]. These sources establish existing admission and filtering
ideas. We did not implement these systems, and the table below cannot rank our
design against them. Their reported production traces and hardware evaluations
are not evidence for this exercise.

The first local policy, CLOCK, keeps scanning until enough payload bytes can be
released. It provides a reference point for uncapped list work. Cap64 stops after
64 reference examinations and bypasses insertion if its selected victims are
insufficient. Victims are not removed unless the scan obtains enough bytes. Bit
clearing and movement of the hand still take effect when insertion is bypassed.
This makes the policy stronger than one that throws away useful objects and then
discovers that it cannot fit the candidate. Cap64 is small enough to implement
without an adaptive controller or a frequency estimator.

Reserve8 separates the request allowance into 48 foreground examinations and
16 maintenance examinations. Maintenance runs after every request, including a
hit or bypass, and attempts to bring the number of free bytes to 8 MiB. It can
stop earlier when that target is reached. When referenced objects prevent
progress, it only clears their bits and advances the hand. The free-space target
is soft: a request can consume the reserve and maintenance may be unable to
restore it immediately. It is therefore incorrect to promise that the next
large object will always be admitted. The specification also includes Reserve4
and Reserve16, changing only the target to 4 and 16 MiB.

There is no detached worker in this design. The maintenance allowance belongs
to the request that invokes it and is included in the work counter. Foreground
victim records are kept in a temporary list and counted only once towards the
bytes available for insertion. The hand must remain valid after their removal.
These details matter because an apparent limit on the foreground loop alone
would omit maintenance work. Both Cap64 and the reserve policies bound reference
examinations at 64 per request. This is not a bound on response time, allocation,
index operations, payload copying, or backend service.

The fixed table contains four scenarios with one million requests each and a
64 MiB cache. The payload classes are 4 KiB, 64 KiB, and 1 MiB. SteadySmall has a
stable small-object working set. MixedBurst introduces short bursts of large
objects. HotShift changes which objects are popular, and LargeReuse frequently
reuses large payloads. These names describe intended situations rather than
available request traces. We have assigned counts for each size class and
computed byte totals from those counts. There are no repeated trials, random
seeds, confidence intervals, machine descriptions, or latency samples.

For MixedBurst, Cap64 has 635,000 hits and Reserve8 has 670,000 hits, giving
63.50% and 67.00% request-hit ratios. Their origin-fetch totals are 97,226.5625
and 81,562.5000 MiB. Cap64's 12,000 budget bypasses fall to 4,000 with Reserve8,
but total reference examinations rise from 12 million to 14 million. CLOCK has
a fixture maximum of 8,192 examinations on one request; both capped policies
have a maximum of 64. That maximum comparison alone does not explain choosing
Reserve8 over Cap64, because the simple cap already provides the same bound.

The other rows are less favorable to a uniform choice. In SteadySmall, Cap64
has 92.25% request hits and Reserve8 has 90.10%, while their average examinations
are 0.82 and 1.80 per request. Reserve8 also fetches more payload bytes from the
origin. In HotShift, the corresponding hit ratios are 58.50% and 60.60%. In
LargeReuse they are 80.20% and 79.80%, despite Reserve8 fetching fewer bytes.
Request hits and avoided bytes therefore need separate treatment. Neither
metric in this fixture establishes user-visible speed or lower deployment cost.

Changing the reserve target exposes another tension. MixedBurst reaches 65.20%
request hits with Reserve4, 67.00% with Reserve8, and 66.20% with Reserve16.
Reserve16 nevertheless has the lowest origin-fetch byte total among those three
rows. In SteadySmall the same targets give 91.45%, 90.10%, and 86.80% request
hits. A larger reserve sacrifices resident contents and may add scanning even
when the service does not need additional free space. The numbers have been
written to contain this behavior; they have not established an optimal target.

Further work would have to turn the specification into an implementation,
collect request streams, and compare published policies under a stated service
objective. At present we can inspect accounting and explain possible failure
paths. We cannot estimate throughput, verify cache-state evolution, establish
generality, or claim that retaining spare capacity is an original idea. The
exercise leaves open whether the additional maintenance is useful when a simple
cap already removes unbounded scans from the request path.
