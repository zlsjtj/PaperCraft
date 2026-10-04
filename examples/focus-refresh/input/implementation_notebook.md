# DEMO implementation notebook — first preserved record

The following entries are a constructed development narrative. They do not record real laboratory dates or actions.

**Entry A, fixture sketch.** Chose nine specimen apertures and a north-of-center bridge clip. Recorded both clip footprint and head envelope. Checked that all acquisition centers fit and that the sample fields sit inside their apertures. Kept the clip as a solid component in the dock frame. Did not infer that an unobstructed endpoint makes its incoming segment safe.

**Entry B, initial map.** Defined the shallow stored residual bowl analytically. Made global xy registration and plane recovery exact so local map reuse could be evaluated without mixing two error mechanisms. Retained the xy transforms and plane coefficients in every exchange record even though they cancel after the common operation. Assigned the common registration a total budget of 5.0 s. No experimental estimate was made for this constant.

**Entry C, first controller.** Implemented ROW3 with the center of each row as the sentinel. Used a strict `>` comparison at 8.0 micrometers. Center readings in triggered rows are reused; untriggered rows keep their whole old map. A thresholdless alternative SHIFT3 copies the observed row displacement to both outer settings. PLANE and ALL9 are also executable policies rather than qualitative comparisons.

**Entry D, case list.** Fixed the following input order before scoring policies. B01–B08 are broad-row changes with nominal row vectors [0,0,0], [0,12,0], [14,0,0], [0,0,-15], [12,0,-14], [0,16,14], [14,-16,15], [-18,14,-16] micrometers. E01–E08 all use row vector [1,-2,2] and add an outer-site offset in rows S,M,N,S,M,N,S,M respectively; their extra offsets are [12,-14,16,-18,20,-22,24,-16] micrometers. C01–C08 use one changed row, plus an outer-site offset on that same row for C01–C04 and on the next row cyclically for C05–C08. The complete exact case parameters are in `events.csv`. The ordered cases are not repeated random trials.

**Entry E, reading construction.** For event ordinal e=1..24, row index r=0,1,2 for S,M,N, and column index c=0,1,2 for W,C,E, texture is `0.35*(((e+2*r+c)%5)-2)` micrometers. Probe noise is `0.15*(((3*e+2*r+3*c)%9)-4)` micrometers. Each policy receives the same m_ej whenever it measures that event/site. These are deliberately transparent bounded patterns, not a stochastic noise simulator.

**Entry F, movement budget.** Implemented a segment–rectangle clipping calculation with boundary contact counted as overlap. The center keepout is the clip footprint enlarged by the square head's half-width. Charged an entire 0.74 s raise/lower operation once per overlapping segment. Used direct return-to-park paths, including the diagonal from NE. Early mental arithmetic overlooked that return segment; the preserved data uses the program's complete segment list. Do not quote a “zero retraction” ALL9 route without checking the return.

**Entry G, records.** Exported all events, all policy/event summaries, all center errors, and all executed local probe/return operations. PLANE has no local trace rows because it has no local waypoints; its run summary remains present. The common acquisition path is recorded in metadata and apparatus notes. Nothing was dropped on focus failure. Timings are sums of specified constants and geometric distances, not clock readings.

**Entry H, unresolved next work.** A physical implementation would need a characterized autofocus routine and actual seating trials. The existing model contains no such experiments. We have not assessed a route optimizer, a recovery policy, a sensor-placement search, additional sentinels, or a learned predictor. Those cannot be described as implemented variants. We have not searched for related systems or determined whether any mechanism is novel.

## File-generation receipt

`construct_demo.py` uses only Python's standard library. It produces 24 event rows, 96 policy-run rows, 864 center-result rows, and a local operation trace. Every data row carries `CONSTRUCTED_DEMO`. The construction has no random seed because it uses no random draws. CSV files use UTF-8 and period decimal separators. The generator refuses to overwrite any of its output filenames in the target directory; regenerate into a new destination and compare hashes. The initial data bundle is `data_v1/`.

## Small hand-check example

At SC, the stored residual is 0.005*24^2=2.88 micrometers. At any event, an observation reports that residual plus the event's constructed local change plus the bounded probe error. ROW3 compares the observed residual with 2.88, rather than comparing the absolute z position with zero. This example only fixes the units and reference frame. Policy/event decisions and all outcomes remain in the complete records.
