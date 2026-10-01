# Framing decision recorded before the first complete draft

This is an editorial self-decision, not human approval. Both passages below were written before first.md. The fixed synthetic evidence, rather than the original title, determines the selection.

## Candidate A: begin with the interrupted update

### Publishing Base-Relative Tile Patches as Complete Raster Revisions

A raster update can arrive one tile at a time even though the display must present a complete revision. If two tiles change together, exposing the first replacement while the second is delayed creates a view belonging to neither revision. Staging a full snapshot already prevents this mixture. We instead stage only the declared replacements against an explicitly named, pinned base, then publish their assembled root together. This preserves the same visible-revision criterion while making transfer proportional to the patch rather than the whole raster. The useful question is when that reduction repays the work of validating and assembling the patch.

## Candidate B: begin with the cost of the already-correct baseline

### When Sparse Transfer Repays the Cost of Coherent Raster Publication

A complete staged snapshot already gives a raster dashboard a coherent new revision. Its limitation is the cost of retransmitting unchanged tiles. In the supplied comparisons, transferring four changed tiles instead of the full raster sharply reduces wire volume, but the same sparse transfer is slower on a fast local link; nearly complete updates are slower as well. These contrasting cases motivate a conditional choice between two coherent methods. A patch names the client revision on which it depends, reuses its unchanged tiles and withholds publication until every replacement validates. The comparison asks which costs change when complete-snapshot transfer is replaced by that dependent update.

## Selection

Select A. Its delayed two-tile operation makes the distinction between arrival and publication visible before introducing the comparison, and its third sentence gives the strong full-snapshot baseline credit for the same coherence property. It connects directly to the pinned-base checks, publication-only acknowledgement and reconnect failures. B makes the adoption boundary immediate, but introduces performance cases before showing why assembling changed tiles needs a named base; it is less effective at revealing the necessary technical work.

A costs an extra operational explanation before the quantitative result. Its risk is seeming to claim coherence as a new primitive. The manuscript must therefore retain the explicit full-snapshot comparison and inherited root-publication mechanism in the opening, and use dense and fast-link losses to delimit the value of sparse transfer. No first-of-kind claim is selected.

## Presentation choice

Keep all 12 source rows in one grouped, numerically aligned Markdown table. Put coherence beside completion delay so IT's faster but mixed views cannot be read as a qualifying speed baseline. Keep payload retention and preparation time in that same table so reductions in transmitted bytes are not mistaken for lower total cost. This task requests no diagram or Word output; no rendered-page aesthetic acceptance is claimed.
