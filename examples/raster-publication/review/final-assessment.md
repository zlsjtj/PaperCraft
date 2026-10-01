# 最终稿匿名评阅与各自首稿比较

## 评阅边界

首次稿评阅保存后，收到明确的最终稿评阅指令。先按 **C → A → B** 阅读各最终稿的标题、摘要和引言，再按同一顺序阅读全文。仍只使用先前允许的五个原始文件、固定评阅问题及六篇匿名稿件；未查看 key、生成身份、skills、decision、自修理由或其他输出。没有修改任何稿件。

这是独立代理进行的匿名模型辅助文本评阅，不能代替真人阅读、作者认可或出版验收。未看到 Word 页面，不作排版结论；没有测量阅读时间，不给总分。不因自修发生就预设质量必然提高，也不根据文风猜测生成身份。

最终稿的 12 个原始记录逐行核对通过：A 为单表 12 行，B 为单表 12 行，C 为 8 行 FS/SP 加 4 行 IT；方法、工作负载、链路以及所有数值均与 CSV 相同，12 个键均唯一。C 拆表没有删去 IT 指标。此验证不将合成数据转化为实际性能证据。

## 先读最终开篇的判断

**A 仍最容易进入。** 它保留了新 A / 旧 B 的具体问题，随后立即说明已有发布保护，再提出复用未变 tile 的剩余问题。摘要把首稿的 `“assembled privately against a named, pinned base”` 改为 `“sharing unchanged tiles from a named, pinned base”`，进一步说明为什么传输可减少；其他开篇结构变化很小，原有进入优势得以保留。

**C 的剩余问题更集中。** 首稿的 completion delay 和 retained payload 并列提问，最终引言改为 `“including conditions where transmitting fewer bytes does not finish sooner”`，使后文负例的作用提前清楚。仍将 64 个指针、4,096 个单元、四字节和完整负载放在简介第二段，首次进入时的规格负担没有明显消失。最终摘要以 `“concrete protocol”` 表达贡献，仍明确继承机制和合成证据，没有把它写成新原语。

**B 更清楚地列出新增决策，但出现一处语义退步。** 摘要现在列出 acknowledged base、coalesced target values、publication 三个决策，比首稿泛称协调 sparse transfer 与 contract 更容易定位实质工作。可是新首句 `“Sparse raster transfer saves communication only if the client can reuse unchanged tiles without exposing a mixture of producer revisions.”` 将“节省通信量”的必要条件写成“无混合版本暴露”。这不成立：原始 sparse/constrained IT 只传 66 KiB，低于 FS 的 1026 KiB，但 IT 只有 71/120 个 coherent runs。节省字节可以与不一致共存；一致性是合格应用方案的要求，不是字节减少的必要条件。首稿首句本来准确地区分了这两者。

## A-final 相对 A-first

### 实际改善

1. **新增工作为何必要，解释得更就近。** 方法加入 `“The published root also determines which unchanged tiles a later patch may reuse. The client therefore acknowledges only after publication.”`，紧接着说明首包 ACK 可能使服务器选择尚未发布的 root。首稿主要到讨论才将这条逻辑收拢；最终稿降低了理解 ACK 规则时的回读需求。
2. **指标口径补齐。** 表注新增 `“preparation is median ms”`，修复首稿 Prepare 列统计量不明的问题；framing、binary units 和单读者释放假设集中在表注，能就近解释数字。
3. **对照资格更早出现。** 表前说明 FS/SP 通过一致性检查，IT 保留是为了显示立即暴露到达数据的后果。随后单独解释 IT 的完整四组计数，包括 fast-local 的 71/120，既没有隐藏较快结果，也没有混用性能基准。
4. **反转与采用边界更具体。** 正文补充 p95 同向改善/反转，并在讨论明确四个 case 无法确定 crossover threshold 或 adaptive selection policy；恢复代价和慢读者驻留被说明为两个不同限制。
5. coalescing 明示 `“sends each coordinate once, using its target-root value”`，比首稿更显式承接 N5 的 once-per-coordinate 事实。

### 保留的弱点与代价

- 引言用 A/B，方法直接切换 a0/a1 的小幅符号跳转仍在；虽能推断，首次出现时定义会更顺。
- 协议段落依然较长，故障处理和历史/coalescing 各承担多种规则。最终排序和因果句已改善理解，但不能据此声称完全无需回读。
- 一致性资格在表前、表注和 IT 分析再次出现，信息略重复；重复服务于防误解，没有发现由此导致的技术退步。

**结论：** 相对自身首稿，A 的改善主要是解释位置与指标口径，保留了原有易读开篇，未发现新增实质科学错误。

## C-final 相对 C-first

### 实际改善

1. **修正内存趋势歧义。** 首稿 `“Payload retention declines ... as changes become denser”` 容易把密度趋势读反；最终改为 `“SP retained payload grows from 1.06 through 1.38 to 1.94 MiB, approaching FS's 2.00 MiB.”`。现在相对 FS 的节省与随密度增长的方向一致，且完整保留读者释放假设。
2. **wire 口径补齐。** 最终表注明确包含 protocol framing，修复首稿遗漏。
3. **比较对象的作用通过组织体现。** 第一表直接配对 FS/SP，第二表保留 IT 的全部数据并说明诊断用途。读者寻找同一保证下的代价比较时更直接；这是文本和表格信息组织的判断，不是 Word 页面布局验收。
4. **一致性指标允许旧 coherent root 更明确。** 最终定义句直接说明有限检查 `“permits an older coherent display”`，减少从方法例子推回指标定义的负担。
5. 对稠密和 fast-link 两组反转同时列出 median 与 p95，功能检查仍保留目标值 coalescing 和 malformed-ID rejection；没有因简化叙事牺牲负例或指标。

### 保留的弱点与代价

- 拆表有收益，也增加跨表比较 IT 与 SP 的查找距离，两个表重复相同表头。对以“先比较合格方案”为目的的主线是合理取舍，不能简单等同于所有读者都更省力。
- 功能 traces 从首稿独立大节移到结果节后部，但最终没有为它单设小标题。正文清楚说 `“Separate functional fixtures”`，未混淆证据；若要快速定位 28 traces 或失败变体，B 的 3.2 标题更醒目。
- 引言的规格数字密集段仍在；最终改写的重点是论证和比较组织，开篇进入负担只部分改善。

**结论：** 相对自身首稿，C 修复了明确的语义风险和口径遗漏，比较组织也更聚焦。代价主要是跨表导航，而非证据损失。

## B-final 相对 B-first

### 实际改善

1. **新增机制更具体。** 标题和摘要围绕 publication contract，并将三个关键决策逐一列出；方法小标题也改成 base reuse、target-value coalescing、staging/retention，便于对应实现责任。
2. **补回实验条件。** 最终评价明确 `“Compression is disabled.”`，首稿遗漏的条件恢复。
3. **内存假设就近。** 单读者在一周期内结束的假设移到表格后，与元数据排除条件在一起，不必读到讨论末尾才正确解释 1.06 MiB 等数字。
4. **计时对象更明确。** `“It is neither first-byte latency nor a measurement of frame rendering.”` 清楚分开 packet application/staging 完成与真正画面渲染耗时，避免由显示问题的叙事误推计时终点。
5. **功能证据边界更易找。** 新增 3.1 合格比较与 3.2 revision-state rules 小节；28 traces、8 次 fallback、无恢复延迟以及不能继承 sparse-path 字节收益在同一功能段落内，优于首稿的分散位置。稠密化时的载荷上升趋势也说得明确。

### 自修引入的退步及剩余限制

- **摘要第一句是需要修正的实质表述问题。** 前述 `“saves communication only if ... without exposing a mixture”` 与 IT 节省字节但不保一致性的固定记录矛盾。全文机制和表格仍然正确，不能用全文可推断正确意思来免除摘要的错误必要条件。可改为：“Sparse transfer can reduce communication, but preserving coherent views also requires clients to reuse unchanged tiles without exposing mixed revisions.” 此为评阅建议，未修改稿件。
- 摘要 `“The advantage reverses”` 紧跟 wire volume 与 completion delay 两个收益，未像首稿那样指明 **latency advantage**。稠密与 fast-local 情形下 wire 仍更少，反转的只是延迟优势。正文数字解释正确，但摘要宜恢复这一限定，避免读成两种收益都反转。
- 尽管摘要决策列表更具体，开篇仍没有 A/C 那样的两 tile 例子；第一个具体示例在方法节。它更适合已经接受 coherent-view contract 概念的读者，首次进入负担仍略高。
- 单固定 schedule、无重复/置信区间等仍主要放在末尾讨论。前面已有 finite fixture 和 synthetic 披露，未越界，但若读者要先判断统计意义仍需向后查找。

**结论：** B 的方法与评价组织有实际改善，首次稿的两个信息位置/条件问题得到修正；同时摘要引入逻辑过强的必要条件，并降低了“哪种优势反转”的精度。因此不能把其自修概括为单向提高。

## 最终横向判断

| 观察维度 | 最终稿表现 |
|---|---|
| 开篇进入 | A 的具体示例和问题→既有保护→剩余问题路径最轻松；C 也具体但规格更早；B 的贡献决策更明确但仍较抽象 |
| 继承与新增 | 三稿均明确既有 publication/immutable-root 基础，均能把新增工作落实为 base、target coalescing、ACK、fallback；没有新原语或首次发明夸张 |
| 必要工作解释 | A 最终把 ACK 因果关系移近规则；B 的细分方法最便于定位；C 的 coalescing、范围检查和功能覆盖表述完整 |
| 合格性能比较 | C 的 FS/SP 配对表最直接表现基线资格；A/B 单表更便于同一 case 内查看全部三种方法，均明确 IT 只是诊断 |
| 数据与范围完整性 | 三稿全部原始记录和核心负例均在；allocation/crash 缺失、finite schedules、stalled reader、fallback 范围均保留；没有真实实验或部署声称 |
| 剩余准确性问题 | A/C 未见新增实质错误；B 摘要首句需要修正，且应限定反转的是 latency advantage |
| 自修收益 | A 改善解释位置和统计口径；C 修复趋势歧义并重组比较；B 改善结构和条件位置但有摘要退步 |

**不强选整体赢家。** A 的开篇与连贯叙述、B 的方法/功能证据检索、C 的合格基线比较各有优势。若立即选取可供下一轮作者审阅的文本，A/C 当前没有本轮发现的新增实质科学表述错误；B 应先修其摘要，而不能仅凭结构更完整判定其整体更好。这是针对这些具体匿名稿件的文本判断，不能外推为某工具、skill 或写作机制稳定胜出，更不能替代作者对最终稿的明确认可。
