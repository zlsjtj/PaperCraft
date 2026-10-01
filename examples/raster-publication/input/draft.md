# A framework for distributed environmental raster visualization

DEMO — invented editorial validation material, not a report of measured research.

## Abstract
The raster service uses a sparse map, sorted messages and an atomic swap and is a complete framework. There are 64 tiles and 4096 cells in each tile. It has a queue, a sequence field, acknowledgement and retry logic. Three workloads are tested. Several network cases have been checked. Good performance is observed and the method is suitable for large remote maps. The patching method is much more efficient than sending a whole raster every time. It keeps the reader responsive. There are some limitations about retained revisions and connection interruptions.

## Introduction
Environmental maps are widely useful. A dashboard displays the newest committed raster revision. Sending each cell individually can give low visible latency. Clients sometimes pause or lose connectivity. Some maps are mostly unchanged between revisions, while a spatial front can alter most tiles. The existing application was built around immutable revision roots, not around the proposed message protocol. Raster values are assumed already computed and are not evaluated here. It is important to visualize them in an efficient manner.

## System
A server has an array indexed by tile coordinates. Each root has an integer revision, and a tile version is read-only after publication. The UI reads one root. There are old and new maps of pointers. There is a touched bitmap, a changed-tile list, an acknowledgement and an epoch number. Packing the full frame is simple. Another option is to send changed tiles and set their pointers as each message arrives. We implemented staged patches and also an ordinary full-frame staging control. The parser validates sizes and checksums. A gap in the revision history can use a fallback. All data are currently lossless. Message order was tested and a reconnect mode was tested.

## Measurements
The table contains the completion latency and bytes. Compared with full-frame transfer, SP reduces bytes a lot in sparse workloads. Patch sizes are larger when nearly everything changes. No compression was enabled. The first byte is not the completion time. The many test traces were created manually; they include duplicates and drops. The published values come from fixed traces; the project has not been deployed. We used two queue budgets during development but did not retune these during the listed comparison. Reader validation records contain failed mixes in one configuration. All valid designs have a cost.

## Discussion and conclusion
The service contains many modules, and the module combination is called a unified framework. An atomic swap has been used. The number of packets and the bitset show the engineering effort. There are comparisons but a larger real-world study is required. Some delays are caused by network conditions. The framework may be useful for dashboards if the state model fits.
