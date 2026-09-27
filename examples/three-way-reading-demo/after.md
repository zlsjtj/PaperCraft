# Introduction

After an input changes, the previous implementation reevaluates every node in the acyclic computation graph. The candidate instead follows successor edges to invalidate affected nodes, schedules only those nodes, and reuses stored results for nodes that remain valid. The central difficulty is deciding whether a stored result can still be reused: equal values do not necessarily have the same dependency versions. Each reuse therefore checks the node’s input signature and dependency versions. These checks, invalidation, and selective scheduling form one execution mechanism. The scope excludes cyclic graphs and changes to graph topology.

# Results

The constructed teaching records show fewer node evaluations when an input change affects only part of a 120-node graph. For a single-branch change, the candidate evaluates 12 nodes versus 120 for full recomputation; for a cross-branch change, it evaluates 48 versus 120. A global change requires all 120 nodes in both implementations. Outputs agree with full recomputation in all three cases, which checks these cases but does not establish general correctness. The counts describe avoided node evaluations, not measured acceleration: signature checking adds work, and wall-clock time, peak memory, and concurrent execution were not recorded.
