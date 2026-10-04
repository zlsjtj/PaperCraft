# Actual entry choices before the complete draft

## A. Marking Durable Progress for Restartable Block Exports

A returned write does not necessarily leave a usable block after a crash. A restartable export must distinguish bytes that have been written from a prefix it can safely keep. We record progress only after synchronizing the output, and validate that record against its named block on restart. The design reduces inspection in the supplied traces, but adds a progress synchronization to every block.

## B. Validated Progress Slots Reduce Restart Inspection in a Block Export

The existing export already recovers correctly by scanning its output for the longest valid prefix. The remaining question is whether it must repeat that inspection whenever it restarts. Two alternating progress slots identify an already completed prefix, allowing restart to validate a recorded boundary before deciding whether the full scan is needed. The constructed traces expose both this reduced inspection and the failures that restore scanning or require replay.

Selected B. A starts with a useful failure but risks making crash recovery itself seem new. B gives the correct scanner credit immediately and makes the actual remaining comparison visible. The complete manuscript still uses the failed write-offset shortcut to explain why the progress boundary must be durable.
