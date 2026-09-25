# 贡献、工程与结果的完整示例

下面使用合成的检查点流水线案例。原始材料在[示例输入](checkpoint-demo/input.md)，英文稿保留论文语言；本节说明修改判断。它们不是公开的科研测量。

## 贡献段：把已有机制与本次变化分开

原文：
> We present a novel reliable checkpoint architecture. Compression and grouping make it efficient.

改写：
> The staging path overlaps compression of independent chunks with writing earlier chunks. Both paths use the same compressor and grouped writes; the change is the overlap between these stages.

原问题是把基线已有的压缩和分组归为新增贡献。改文指出串行路径的约束和新的执行关系。依据是输入 E1、E2；它说明给定设计差异，尚不证明文献首创或独立组件加速。

## 工程段：从部件清单到必要条件

原文：
> Every checkpoint has a generation. Results carry an ID and generation. The writer checks them.

改写：
> A recycled buffer must not accept a late result from its previous owner. Admission therefore checks both the chunk ID and checkpoint generation against the current slot. The checksum is checked before commit, and the buffer is released only after writing completes or cancellation invalidates ownership.

改文用取消重启中的迟到结果解释双匹配、校验和与释放条件。依据是 E3；这是协议说明，不是新实现、穷尽证明或掉电恢复实验。

## 结果段：让收益与损失一起回答问题

原文：
> The throughput gains were 11.11%, 5.26% and -9.09% on three data sets. Therefore our method is widely useful and consistently faster.

改写：
> Forced staging reduced median elapsed time from 10.0 to 9.0 s for A and from 20.0 to 19.0 s for B, but increased it from 1.0 to 1.1 s for C. For equal work, these correspond to throughput changes of 11.11%, 5.26%, and −9.09%. Each median uses five runs; the measurements exclude file creation and cleanup and use one fixed thread count.

改文保留全部三例，明确相同工作量、计时范围和重复单位。依据是 E6。阈值来自同组三输入初测，强制路径结果不冒充独立测试过的阈值策略；损失原因仍未测明。

## 图表组织

机制图应展示串行压缩后写入与相邻阶段重叠的具体对应，用同一批块比较。结果图保留 A、B、C，写清时间或吞吐比方向，标出持平线。没有逐次运行数据就不补误差条，不用透视放大收益。图源与图注、正文应共同说明这是教学数据。

完整三段候选及逐项依据见[改稿](checkpoint-demo/revised-three-paragraphs.md)和[中文记录](checkpoint-demo/change-record.zh.md)。继续修改时参见[续改判断](actual-continuation-revision.md)。
