# 贡献、工程与结果的完整示例

下面使用合成的检查点流水线案例。原始材料在[示例输入](checkpoint-demo/input.md)，英文稿保留论文语言；本节说明修改判断。它们不是公开的科研测量。

## 贡献段：把已有机制与本次变化分开

原文：
> We present a novel reliable checkpoint architecture. Compression and grouping make it efficient.

改写：
> The staging path overlaps compression of independent chunks with writing earlier chunks. Both paths use the same compressor and grouped writes; the change is the overlap between these stages.

原问题是把基线已有的压缩和分组归为新增贡献。改文指出串行路径的约束和新的执行关系。依据是输入 E1、E2；它说明给定设计差异，尚不证明文献首创或独立组件加速。

## 准确但主次分散的入口

以下两段都只使用前述 DEMO 的 E1–E3、E6–E7，不把“原文错误”作为唯一试题。

原段：
> The staging queue tracks chunk IDs and checkpoint generations, verifies checksums, and admits results into reusable buffers. It overlaps compression and grouped writes. Targeted injection rejects stale generations, wrong IDs and checksum mismatches. Forced staging reduces median time for A and B but increases it for C. The compressor and grouped writes are unchanged.

改段：
> The staging path lets later chunks be compressed while earlier chunks are being written. It retains the same compressor and grouped writes; the change is their overlap. Reusing buffers after cancellation requires matching each result to its current chunk and generation before admission. Targeted injection checks this ownership rule, while the three-input timing comparison shows gains for A and B and a loss for C.

第一句先给读者可理解的变化，随后区分继承内容、必要工作与两种不同证据。校验和细节、具体时间、五次中位数和计时排除仍在[完整改稿](checkpoint-demo/revised-three-paragraphs.md)的方法与结果，不能凭这段删去。这个示例展示组织决策，不提供固定句型，也不表示技能已经通过真实读者实验。

## 同一组事实，两条有区别的叙事路线

以上检查点 DEMO 也可从困难进入：

> In the sequential path, writing a chunk waits for its compression to finish. Staging allows later chunks to be compressed while earlier chunks are written, without changing either the compressor or grouped writes. Cancellation makes buffer reuse the difficult part: a late result must not enter a slot that now belongs to another chunk or generation. Targeted injection checks this admission rule. The three-input comparison finds shorter median times for A and B and a longer time for C.

这一稿先建立等待关系，再引出重叠及复用风险；上面的改段直接从新增操作进入。两者使用同一 E1–E3、E6–E7。面对不了解流水线的读者，前者给了为什么需要改变的起点；读者已经知道串行约束时，前一句可能多余。应比较实际材料后的理解记录，不能事先宣称某条路线总胜出。

具体时间与五次中位数仍在结果段，校验和在方法段。入口出现“目标注入检查”不意味着协议已经被穷尽证明，也不把三输入收益写成广泛加速。这种取舍体现信息顺序，而不是为了短而删除证据。

## 标题与证据对象

同一检查点 DEMO 的候选标题 `Buffer reuse accelerates checkpointing` 把收益归给复用，但 E6 比较的是强制 staging 路径与串行路径，且 C 变慢。`Verified fast checkpoint architecture` 又把定向错误注入扩大成整体认证。

较合适的标题是 `Overlapping chunk compression and writes with guarded buffer admission`。它将 E2 的执行变化放在前面，E3 的接收条件作支撑，不把未隔离的组件收益写成已测因果。“Guarded”指已描述的接收检查，不是穷尽正确性。若文章重点是该协议性质而且具备相应证明，以性质为中心的标题也可能更好；不能把这个示例固化为禁止机制标题。

其后使用前述实际贡献段和全部 A/B/C 结果即可，不能为了让标题听起来更强而重新包装样本或删掉损失。该例说明证据对象与词语修饰对象的检查，不证明这一个标题已获读者偏好。

## 工程段：从部件清单到必要条件

以下展开用于方法，不作为贡献段的默认长度。贡献入口先给实际变化，支撑设计移到相应方法位置。

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

## 独立上下文中的完整局部试用

[双通道读出示例](optical-readout-demo/README.md)保留原始事实、原段落、从动机进入和从检查进入的两稿。它检验完整关系展开，篇幅增加是明确代价；不能把它当作“首读简洁”的成功模板。不是只提供可替换名词的漂亮句式。

## 完整但重点分散时

参见[固定开口示例](aperture-focus-demo/README.md)。它给出旧段、实际入口、后续模型段和图注；不是只有漂亮首句。比较入口与全文两种长度，确认模型条件确有去处。图例是构造的二维教学内容，不主张研究创新或实验工作量。

## 操作先于清单的结构示例

[两芯电缆](cable-demo/README.md)对比完整段落与同尺寸图：先解释只改变什么、保留什么，再交代材料层级。它检验结构叙述与跨题材迁移，不提供科研工作量或效果测量证据。

## 操作与对象关系共同承担解释

[过滤盒实例](filter-cartridge-demo/README.md)从组成清单转向具体更换操作，保留停流与证据边界；记录新上下文试用及需要反馈的部分。
