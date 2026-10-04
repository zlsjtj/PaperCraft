# Restart notes for a twelve row raster acquisition job

Synthetic engineering DEMO. All observations below come from a deterministic local model and constructed fault cases. No equipment, measured workload, external dataset, or real publication is represented.

## Abstract

This note examines an interrupted raster acquisition job with twelve rows and sixteen positions per row. We kept several restart implementations because their buffer sizes and completion times were different. One implementation stores each record immediately, another stores complete rows, and a third stores groups of four records together with a row checkpoint. The calculations include return to a known position after an interruption. Twelve deterministic interruption schedules were evaluated, with no physical apparatus involved. Complete output contained 192 records in the model cases. The no interruption completion times were 2448.0, 2553.6, and 2508.0 ms for row, record, and block storage respectively. Their order changed for some interrupted schedules. A separate constructed case assigned eight records to incorrect positions when anchoring was omitted. The implementations, interruption assumptions, coordinate map, and limitations are documented, although write latency and physical behavior still require experimental investigation before deployment conclusions can be drawn.

## 1 Introduction

The working buffer was initially allowed to hold a complete row. This is 4096 payload bytes because a record contains 256 bytes and there are sixteen records in one row. Reducing this allocation was attractive for a controller that might have other buffers, although no particular controller is evaluated here. The record implementation needs only 256 payload bytes, and the block implementation needs 1024. Headers, the motion state, and the runtime stack are additional allocations. Buffer size alone therefore does not identify the smallest complete implementation.

A raster acquisition job is a useful setting for thinking about restart because previously stored output and present head position are separate things. We consider a carriage that visits an array of fixed positions, producing a record at each one. A loss of supply removes volatile data and the remembered coordinate. There is no physical carriage in the evidence package. Its behavior is specified as a discrete event model, with a separately constructed coordinate error case. The word acquisition denotes a model event rather than a measurement from an instrument.

The immediate record implementation was included even though it needs more commit operations. It is a simple alternative when a medium can finish a small write quickly. The row implementation had already been used in the demonstration scaffold, with two alternating checkpoint slots. The block implementation was then added to the scaffold. These statements describe the local construction history in [S2]; they do not establish historical originality beyond this DEMO or a comparison with published restart systems.

There were also several unsuccessful expectations during the work. We expected fewer repeated acquisitions to imply a shorter job, but the two quantities can disagree after a cut changes the phase of subsequent events. A checkpoint can survive while the physical location remains unknown. We therefore kept time accounting and coordinate assignment as separate checks. The rest of this note records the geometry, storage procedures, and result tables, with implementation details repeated where they affected interpretation.

## 2 Method and implementation details

The array has rows numbered zero through eleven and columns numbered zero through fifteen. Column pitch is 4 mm and row pitch is 6 mm, so the sampled extent is 60 by 66 mm. These dimensions locate sample centers rather than the outside dimensions of a manufactured fixture. Even rows run from column zero to column fifteen. Odd rows run in the opposite direction. Let k denote a position in traversal order within a row. Its physical column is k on an even row and fifteen minus k on an odd row. Global ordinal sixteen times the row plus k provides a monotonically increasing logical key [S1].

[[FIGURE_1]]

Figure 1. Original raster sketch supplied with the DEMO. The drawing combines sample centers, traversal order, and one constructed restart state. Its marked interruption is a state illustration rather than a timed event selected from Table 1.

Every startup spends 120 ms homing. Entering a row, including entering the unfinished row after restart, costs another 30 ms for a row anchor operation. This operation includes travel from the known reference to the first missing position. It is deliberately charged the same amount regardless of travel distance. Each acquisition then costs 10 ms, including its local move. A power cut terminates the current event and all uncommitted volatile samples disappear. Elapsed off time is excluded from powered time; a separate column adds 40 ms for every encountered cut [S1, S3].

AR appends one self validating record after each acquisition. Its commit costs 0.8 ms, and a completed append advances the durable prefix by one ordinal. RC holds sixteen samples and performs a 4 ms row commit. The row payload is staged before publishing its row checkpoint, and an interrupted commit does not publish that row. The RC event combines staging and checkpoint publication into an all or nothing logical outcome. This abstraction is not a claim that a storage medium atomically writes a complete 4096 byte row.

BS collects four successive records, writes their 1024 payload bytes, and publishes a seal. The combined event costs 2 ms. Each seal includes epoch, row, block index, record count, and payload checksum information within a 24 byte metadata allowance. Four sealed blocks cover a row. A separate 1 ms checkpoint update then advances the row cursor. RC and BS retain the scaffold's two alternating 64 byte checkpoint slots. A valid newer slot supersedes the older slot; a torn newer slot leaves the older valid slot usable. The local slot example uses a generation counter and checksum [S2, S4].

After restarting, BS first reads the valid row checkpoint and then examines block seals in the indicated row. A candidate must have the expected epoch, row, block number, four records, payload length, and checksum. Recovery accepts a contiguous prefix beginning at block zero and stops at the first invalid or absent block. A valid later block cannot bridge a hole. If all four blocks survived but the row checkpoint did not, recovery can finish the checkpoint and enter the next row. Lookup costs after a cut are 4, 1, and 6 ms for AR, RC, and BS respectively. Initial startup does not charge recovery lookup.

The illustrative state in Figure 1 has completed rows zero through four. It is in row five, whose first physical column is fifteen. Blocks zero and one, covering traversal positions zero through seven, are sealed. Positions eight and nine were acquired into volatile memory; position ten was interrupted. Consequently, restart begins with traversal position eight, which is physical column seven, at x equal to 28 mm and y equal to 30 mm. The row entry reference is column fifteen at x equal to 60 mm. The interrupted physical column is five. The recovered logical prefix cannot itself reveal a safe physical starting coordinate.

[[FIGURE_2]]

Figure 2. Original storage and restart sketch. Persistent blocks and alternating row checkpoints are distinct objects. The validation path determines accepted output; the anchor operation establishes the coordinate used for subsequent acquisition.

For accounting, each completed event contributes its full configured duration, while the event interrupted by a cut contributes only time spent before the cut. Equation 1 states that rule. E_done and E_cut contain completed and interrupted event instances, d is configured duration, and tau is elapsed duration within an interrupted event. An exact equality between a cut time and the scheduled end of an event is treated as interruption before publication. The event ledger records the convention explicitly.

[[EQ1]]

No erase time, wear effect, overlap between events, cache hierarchy, or communication delay is included. All operations are serial. The cost values were chosen to make the tradeoffs inspectable and are not calibrated. For the model, an accepted record is keyed to a unique ordinal. Reacquired completed records means completed acquisition events minus 192; partially completed acquisitions are excluded from that count even though their consumed time remains in powered time.

## 3 Results

Table 1 lists all twelve trace profiles rather than averaging them into a single score. Each cut time is measured on a cumulative powered clock, which continues across restarts but pauses during off intervals. Every policy receives the same absolute cut times within a profile. Different event durations therefore allow a given cut to strike different phases. T6 through T11 form six regular two cut probes with spacings from 500 to 1000 ms. They accompany the initial six profiles to expose phase dependence; the collection is not a sampled outage distribution [S3].

[[TABLE_1]]

Table 1. Powered completion time in the synthetic model. All 36 policy by trace cases finish with 192 durable logical records. The complete event ledger and repeated acquisition counts are supplied separately. Times are deterministic calculations, not means of repeated physical trials.

In T0, RC needs 2448.0 ms, compared with 2508.0 ms for BS and 2553.6 ms for AR. The BS difference relative to RC is 60.0 ms. For T9, the values are 2885.0, 2836.0, and 2876.0 ms for RC, BS, and AR. BS is 49.0 ms below RC and 40.0 ms below AR in that particular trace. These differences should be read together with T10, where RC needs 2697.0 ms and BS needs 2879.0 ms. Cut phase affects more than the count of interruptions.

The larger number of interruptions in T5 gives 5449.0 ms for RC, 4138.0 ms for AR, and 4194.0 ms for BS. Completed reacquisitions are 140, zero, and eleven respectively. AR thus retains an advantage over BS there. T1 offers a different caution: AR repeats one completed record, BS repeats two, and RC repeats eight, yet RC finishes first at 2821.0 ms. Write cost and the interrupted phases must be included before drawing a timing conclusion from the repetition counter.

We ran sixteen named checks of the local model, including a finite sweep of 128 single cut positions for each policy. Those 384 sweep cases reached 192 durable records. The other checks cover coordinate uniqueness, odd row mapping, analytic no cut totals, seal rejection, a hole in the sealed prefix, and checkpoint slot selection. This is a finite implementation check, not exhaustive verification against every possible cut or corruption. The event simulator uses durable prefix counts; the separately tested seal routines exercise the byte checksum and metadata acceptance rules [S4].

The anchoring control starts at the constructed row five state and injects a residual displacement of positive 4 mm after reset. It examines the eight remaining positions of that row. With anchoring, zero records are assigned to the wrong physical column. Without anchoring, all eight are shifted by one column. This is a prescribed fault injection in coordinate arithmetic, not a measured frequency of positioning failure. A correct payload checksum would not detect this error because the bytes can be intact while describing the wrong location.

## 4 Discussion

The storage allowance for a completed job is 49280 bytes for RC, 52224 for AR, and 50432 for BS in the simplified accounting. RC uses the payload array plus 128 checkpoint bytes. AR uses 192 records of 272 bytes. BS uses 48 blocks of 1048 bytes plus the checkpoint pair. These figures exclude allocation alignment and a filesystem. They also do not predict write latency. In particular, assuming that fewer persisted bytes directly produce the configured timing ratios would add an unsupported explanation.

The lookup and anchor events can themselves be interrupted. In that case, their partial durations are charged and the next startup repeats the required work. No record becomes durable during either event. This is why counting successful homes, anchors, or commits and multiplying by their full durations is insufficient for a trace with cuts. The ledger retains the partial events rather than merging them into a generic restart penalty. An outage during homing is also admissible in the finite sweep, although the twelve main profiles do not attempt to represent every such sequence.

We have only one geometry, one record size, and one set of event costs. The model has no nonrepeatable acquisition effect and no requirement that readings at different times represent the same changing object. Repeating a sample is therefore permitted. A moving target, destructive probe, or external side effect would require a different correctness definition. Similarly, a real storage system needs an explicit ordering guarantee between payload durability and seal publication, which the combined seal event currently supplies by assumption.

The original row checkpoint mechanism remains in BS, and its recovery rules are still needed. The four record seal path adds another persistence boundary and more recovery conditions. The checkpoint reader also runs when no useful block survives. Small write cost, available volatile storage, and the interruption process all affect the available alternatives. We have not swept those costs or changed the geometry. Consequently, the regular probes describe only the configured instance, and implementation costs would require calibration in a subsequent physical study.

## 5 Conclusion

The DEMO provides three implemented accounting paths for the same 192 position raster job. They differ in durable granularity, buffer allocation, and restart work. Across the supplied deterministic traces, no single policy has the shortest powered completion time everywhere. Recovery also needs a position establishing action under the stated displacement fault. The available evidence consists of local calculations, event ledgers, finite model checks, and a constructed failure control. Hardware timing, endurance, real outage behavior, and originality relative to published systems remain untested.

## Internal sources

[S1] specification.md and data/parameters.json. Constructed geometry, state semantics, timing assumptions, and scope. Synthetic DEMO sources created for this package.

[S2] implementation_log.md and model.py. Local construction record and executable model. No external project history is claimed.

[S3] data/traces.json, data/results.csv, and data/events.csv. Deterministic trace definitions and generated accounting results.

[S4] tests/test_results.json, tests/single_cut_sweep.csv, and data/anchor_control.csv. Local finite checks and prescribed coordinate fault injection. These are not experimental receipts from equipment.
