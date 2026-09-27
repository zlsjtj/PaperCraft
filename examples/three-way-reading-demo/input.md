# 固定输入：增量图执行教学例

全部内容是维护者构造的教学材料，不是真实研究或新实验。不要查外部文献或加入优先权主张。

目标读者了解计算图，但不了解该实现。旧方案在一个输入改变后重新执行整个无环计算图。候选维护每个节点的输入签名，沿已改变节点的后继关系传播失效，只调度受影响的节点。未失效节点重用已有结果。真正困难是判断何时可以重用：两个值相等不代表其依赖版本仍相同；每次重用都检查输入签名和依赖版本。动态改变图结构和有环图不在范围内。不要把“先检查签名、再传播、再调度”拆成三个独立创新。

给定教学记录共三类输入变化，每类图均有120个节点。单分支改变：候选执行12个，旧方案执行120个；跨分支改变：候选执行48个，旧方案执行120个；全局改变：两者均执行120个。三类输出值均与完整重算一致。没有墙钟计时、峰值内存或并发执行记录。检查签名需要额外工作，减少节点数不等于已经测得加速。只能报告这三类构造记录，不推出一般正确性证明。

原引言段：The implementation stores signatures and dependency versions. It has an invalidation procedure and a scheduling procedure. It also stores node results. The graph is acyclic. A previous implementation evaluates all nodes after an input changes. The implementation can reuse node results. It checks signatures and dependency versions and walks successor edges. Dynamic topology is not handled.

原结果段：There are 120 nodes. The counts are 12, 48, and 120 for the candidate, and 120, 120, and 120 for recomputation. There are three cases. The outputs agree. Runtime and memory were not measured. There is overhead for checking signatures. The method has good efficiency.

请分别改写引言和结果段，使技术改变、必要判断和已有证据更容易理解。保持英文，不增加事实。每段至多180词，这只是统一比较上限，不是必须写满的目标。
