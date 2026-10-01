# 首次稿开篇匿名评阅

评阅范围：仅按 **C → A → B** 顺序阅读三个 `first-front.md`；本记录在读取原始材料和全文之前写成。未读取作者身份、生成配置或其他评阅。以下是模型辅助文本评阅，不是人类认可、实测阅读时间或 Word 排版验收。此阶段只能判断开篇怎样提出论证，不能验证其技术主张与原始证据是否一致。

## C：问题与公平对照清楚，开篇负担稍高

- **读到的问题：** 分块数据已经到达，不等于一个完整生产者版本已经可见。`“exposes (a1, b0), which belongs to neither revision”` 让失败状态具体可见；同时注明示例不是计时观测，证据边界清楚。
- **真正改变：** 在已有 immutable-root renderer 上增加指定基版本的补丁传输、私有准备与完整发布。摘要直接说明 `“neither dirty-tile tracking nor atomic publication is new”`，没有把继承机制包装成新贡献。
- **公平对照：** `“Full-snapshot staging provides the strongest simple comparison because it already preserves root coherence.”` 是三篇中最直接的比较理由之一。它把优势问题落到完成延迟和保留负载，而不是仅以击败不连贯的立即更新方式证明价值。
- **价值：** 稀疏、受限链路情形下完成更快；完整快照仍有其适用情形。摘要交代 dense changes 和 fast local link 均会反转优势，读者不会先形成无条件加速的印象。
- **边界及负担：** 合成数据、环境数值准确性、基版本可用性、准备成本均有交代。但第一节第二段一次列出 64 指针、4,096 单元、四字节、1,048,576 字节，以及多项继承设施，打断了问题→方法的衔接。`“retained payload”` 被引入为比较维度，开篇尚未解释其口径。标题的 `“Staging Base-Referenced Tile Patches”` 比正文小标题更难直接进入。

## A：最容易进入，继承与增量界面紧凑

- **读到的问题：** `“If A arrives first and its pointer becomes visible immediately, the display can combine new A with old B.”` 不借助字母下标或参数即呈现故障；紧随的 `“Withholding the replacements until both are ready preserves revision 10 during transfer and exposes revision 11 afterwards.”` 给出了直观修正。小标题 `“Arrival is not a complete revision”` 准确压缩了问题。
- **真正改变：** 摘要中的 `“assembled privately against a named, pinned base”` 与 `“every declared replacement validates”` 给出具体新增约束；第二段再界定 root publication、引用计数、dirty-tile tracking、checksums 是继承设施。这里能够较早分清原系统已经会什么、传输协议还需做什么。
- **公平对照：** `“coherence alone therefore cannot establish an advantage for a patch protocol”` 明确阻止把一致性本身当成优于快照的理由。全文将比较三种方法的预告简洁且充分。
- **价值：** 同一摘要内给出相对完整快照的延迟和传输量两个尺度，并同步交代稠密更新和快速本地链路更慢。`“specific transfer design and its conditional cost comparison”` 将贡献范围收得具体。
- **边界及负担：** 合成 fixtures、非新 atomic-publication primitive、非实证服务性能、栅格科学准确性不在范围内，均能读到。开篇没有像 B 那样明确否认已建立 research novelty；但也没有宣称已证明新颖性。摘要的 reconnect controls、base validation、acknowledgement after publication 略提前引入技术细节，正文尚未解释，但没有形成 C 那样的规格数字密集段。

## B：证据性质交代最充分，问题示例较抽象

- **读到的问题：** 网络可延迟或重排消息，逐块传输可能导致新旧 tile 混显。`“the renderer can observe an old tile beside a new tile before the update finishes”` 明确，但没有 A/C 的两 tile、两 revision 例子那么可追踪。
- **真正改变：** 在既有 coherent-view contract 上协调稀疏传输，明确涉及 acknowledgement、coalescing、fallback。`“rather than in introducing a new atomic-swap primitive”` 清楚切开继承基础与新增工作。
- **公平对照：** `“Full snapshots supply the coherent comparison; immediate installation reveals the consequence of omitting staging.”` 把两类对照的用途区分得最整齐，避免将较弱对照当作唯一基准。
- **价值：** 120 prescribed runs 的连贯性、受限链路下传输量与延迟收益、两类优势反转场景并列出现。数字是明确的 authored fixtures，没有写成实际系统统计结论。
- **边界及负担：** `“they establish neither empirical performance nor research novelty”`，以及 `“synthetic fixtures and hand-authored functional traces”`，是三篇最明确的证据来源和能力边界。但摘要的 coordination、coherent-view contract、coalescing、fallback 等术语集中，第一节也持续采用抽象概括。通用标题 `“Introduction”` 没有进一步降低进入负担。

## 开篇比较结论

**A 最容易进入。** 依据是其“新 A + 旧 B”句与紧随的“暂存到齐后再发布”句，问题和方法在一个段落内自然闭合；随后立即说明原系统已有发布机制，再提出复用未变 tile 的剩余问题。此判断来自文本结构，不是计时实验，也不构成全文胜出结论。

C 在最强简单对照及条件性价值上尤其直接，但过早出现存储规格与设施清单。B 对证据来源、新颖性限制及两类基线角色的说明最完整，却要求读者较早掌握协议术语。三篇均能让读者读到：一致性不是独创点，稀疏传输收益有条件，数值为合成材料。原始材料核对前，不能据此判定技术正确、协议完备或负例覆盖充分。
