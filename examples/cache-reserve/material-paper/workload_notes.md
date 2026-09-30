# Scenario and field notes — FICTIONAL DEMO

All 20 rows are hand-assigned illustrative outcomes. They were not generated
by replaying the hypothetical policies. No per-request ordering or realizable
cache-state trajectory is supplied. All rows have `evidence_kind` equal to
`FICTIONAL_DEMO_NOT_MEASURED` and `repetitions` equal to 0.

Four scenarios, five policies, 1,000,000 requests per scenario/policy row.
Numbers include cold start. The payload size of an immutable key never changes.

| workload | requests_4k | requests_64k | requests_1m | Intended situation |
|---|---:|---:|---:|---|
| SteadySmall | 800000 | 180000 | 20000 | Stable repeated small-object working set |
| MixedBurst | 600000 | 300000 | 100000 | Small/medium reuse mixed with bursts of large objects |
| HotShift | 500000 | 400000 | 100000 | Popular-key set changes within the scenario |
| LargeReuse | 200000 | 300000 | 500000 | Frequent repeated requests for large objects |

These descriptions are qualitative conditions, not trace-generation recipes.
There is no claimed probability distribution, dataset owner, seed, real
customer, arrival rate, concurrency level, hardware, or execution date.

## CSV semantics

- `capacity_bytes`: resident payload capacity, identical across policies.
- `reserve_target_bytes`: soft free-space target; 0 for CLOCK and Cap64.
- `requests_*`, `hits_*`: request and hit counts in the three exact size classes.
- `requests_total`, `hits_total`, `misses_total`: sums and complements.
- `request_bytes`: sum of all requested payload sizes, counting repetitions.
- `origin_bytes`: sum of missed payload sizes, counting repeated fetches.
- `hit_ratio_pct`: `100 * hits_total / requests_total`.
- `origin_mib`: `origin_bytes / 2^20`, displayed to four decimal places;
  integer `origin_bytes` is authoritative. MiB is binary, not decimal MB.
- `budget_bypasses`: misses rejected at the foreground examination allowance.
- `examined_entries_total`: total foreground plus maintenance examinations.
- `mean_examinations`: `examined_entries_total / requests_total`.
- `max_examinations_one_request`: assigned maximum, not a latency percentile.
- `repetitions`: 0, because there have been no runs.

Size-class counts, examinations, bypasses, and maxima are manually authored
fixture primitives. Ratios and byte totals are arithmetic derivatives only.
No confidence intervals or statistical significance can be obtained from these
rows. Identical requests counts are intended for comparisons, but identical
request sequences cannot be certified without actual traces.
