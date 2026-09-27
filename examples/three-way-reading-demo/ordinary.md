# Introduction

After an input changes, the previous implementation reevaluates the entire acyclic computation graph. The candidate instead propagates invalidation along successor edges from changed nodes and schedules only affected nodes, reusing stored results elsewhere. The essential decision is whether a stored result is still valid: equal values alone do not imply unchanged dependency versions. Each reuse therefore checks both the node’s input signature and its dependency versions. These checks, invalidation propagation, and selective scheduling form one mechanism for deciding which results can be reused. The implementation assumes a fixed graph topology and does not handle cycles.

# Results

In three constructed cases, each containing 120 nodes, the candidate evaluated 12 nodes after a single-branch change, 48 after a cross-branch change, and all 120 after a global change; full recomputation evaluated 120 nodes in every case. The candidate’s outputs agreed with full recomputation in all three cases. These records show reduced node evaluation counts for the two branch-change cases and no reduction for the global change. They do not establish measured speedup: signature checks add work, and wall-clock time, peak memory, and concurrent execution were not recorded. Agreement in these three cases also does not constitute a general correctness proof.
