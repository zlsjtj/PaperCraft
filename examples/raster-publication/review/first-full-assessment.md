# 首次完整稿匿名评阅

## 范围和方法

已先按 C → A → B 只读开篇并保存 `front-assessment.md`，再读取 `paper-input` 中的 `task.md`、`draft.md`、`implementation.md`、`notebook.md`、`results.csv` 和根目录的 `review-questions.md`，最后按 C → A → B 完整阅读首次稿。本记录只评首次稿；未读取最终稿、生成身份、key、skill、decision、自修理由或其他输出。

三稿表格均逐行与原始 CSV 核对，另以只读脚本核对 12 行的工作负载、链路、方法及全部数值：三稿均为 12/12 行，未发现转录差异。文中百分比 80.5% 与 93.4% 与对应原始值相符。这只能确认这些固定合成数据的转录和计算，不能证明实际性能或普遍正确性。

这是模型辅助文本评阅，没有 Word 页面，不作排版验收；不报告虚构阅读时间、人类认可或泛化美学总分。所有比较以相同原始材料和首次稿阶段为限，不识别三稿生成条件，也不强选整体胜者。

## 三稿共同完成的实质改进

原稿以 `“a complete framework”`、模块清单及 `“much more efficient”` 概括工作，不能说明继承基础、增量设计与代价如何相连。三稿都改为可核对的论证：立即安装 tile 会出现不存在于任何生产者版本的混合 root；完整快照已解决这一问题；新增协议要在指定 base 上复用未变 tile，私有组装 target，并公平比较保持一致性的完成成本。

开篇问题、既有保护、额外权衡均可定位：

| 稿件 | 保护读者免受何种问题 | 既有保护 | 新增权衡 |
|---|---|---|---|
| A | `“the display can combine new A with old B”` | `“The existing service already supports that publication boundary.”` | `“whether unchanged tiles can be reused without making incremental network arrival visible, and when doing so reduces completion cost”` |
| B | `“the renderer can observe an old tile beside a new tile”` | `“The application studied here already addresses local consistency.”` | `“Full snapshots supply the coherent comparison; immediate installation reveals the consequence of omitting staging.”`，结合摘要中的 conditional tradeoff |
| C | `“exposes (a1, b0), which belongs to neither revision”` | `“The existing service already supplies the essential rendering abstraction”` | `“whether transferring only changed tiles can preserve that behavior at lower completion delay and retained payload”` |

三稿均保留原始 DEMO 披露，没有增加真实文献、外部实验或实际部署结论；均明确 root publication、引用计数、root copying、dirty tracking/sparse invalidation、checksums 是继承设施。没有把已有原子发布称为新 primitive，也没有用缺少文献调查来证明新颖性。

## 科学语义与证据范围

| 核对项 | 三稿实际表现 | 判断 |
|---|---|---|
| base / changed / target | 均说明 manifest 的 base、target、changed set；固定可见 base，共享未变 tile，私有放入 target replacements | 与 I2–I3 一致 |
| 未变 tile 的创建版本 | A/C 明示 revision 11 可保留 revision 8 的 tile；B 明示可保留若干版本前的 tile | 没有把“root 一致”误写成“所有 tile 时间戳一样新” |
| coalescing | 均保留 touched-coordinate union、发送 target 值、可能保留已恢复旧字节的坐标 | 保留了非最小差分压缩器这一限制 |
| 历史与恢复 | 均保留最多八个已完成版本、只确认已发布 root、base 无效时 FS、重复/冲突/乱序/晚到消息与断线处理 | 必要协议行为基本完整，没有无限历史或持久事务暗示 |
| 一致性、完成时间与传输量 | 均定义完成起止点；一致性检查覆盖规定的中间 reader interleavings，而不只看最终 root；均拒绝把 IT 当作有效的一致性性能基线 | 重要证据层次没有混淆 |
| 内存 | 均给出 512 字节指针表和 4,096 字节附加元数据；载荷数字排除这些开销；均保留单读者及时释放与 stalled-reader 无界限保证 | 未把 payload 峰值说成总内存上界；局部口径问题见下文 |
| 表内负例 | 均保留 dense 97 对 91 ms，以及 fast-local 2.6 对 2.2 ms 的反转 | 没有只报告受限链路稀疏收益 |
| 调度与覆盖 | 均保留 fixed schedule、有限 interleavings、无重复/置信区间/随机丢包模型/CPU 微架构研究，以及 fast-local 只有 sparse | 没有从有限 fixtures 推出所有调度均正确 |
| 功能证据 | 均与表内 120-target 数据分开说明 28 条手写 trace、8 条 FS fallback、移除 base check 的 2/6 失败、首包即 ACK 的 1/6 失败 | 没有合并样本或称作计时消融；无恢复延迟结果与 fallback 无法继承稀疏收益均保留 |
| 未实现检查 | 均保留 allocation-failure injection、process-crash 测试缺失；security/authentication/Byzantine 在范围外 | 没有声称生产就绪 |

完整正文没有发现改变原始数值、夸大成真实实验或颠倒核心协议语义的错误。三稿对性能归因也都保留边界：A 的 `“These are whole-method comparisons”`、B 的 `“the fixtures do not isolate latency causes”`、C 的 `“do not isolate those components' causal contributions”` 均阻止把全部差异归结为字节数或准备时间。尤其不能由准备时间差直接解释完整完成延迟差，三稿未作这种定量因果承诺。

## A：开篇负担低，讨论将新增工作连接到必要性

**优点。** 开篇用 A/B 两块的具体失配建立问题；方法节再引入规格数字，使读者先理解失败为何重要。最有价值的工作量呈现不是模块数量，而是讨论中的两句：`“unchanged data acquire meaning from a particular base”`，以及 `“publication-only acknowledgement keeps future coalescing tied to the client's actual visible state”`。它们把 base validation 和 ACK 时机解释成正确重建后续 target 所必需的约束。协议功能失败随后为这两个约束提供有限证据，未包装成普遍证明。

表格标题就交代 retained payload 排除元数据及单读者假设，读者读取数字时不用等到讨论才知道它们不是总内存。正文也直接把 sparse-path 字节收益与 fallback 分开。

**局部损失或可改进点。**

- 表头 `“Prepare ms”` 和表注未说明它是 **median**。源 CSV 是 `median_prepare_ms`；值未错，但统计口径不如 B/C 完整。补一个词即可解决。
- 简介只称 tiles A/B，方法接着写 `“the visible pair remains (a0,b0) while a1 waits in private state”`，没有就地明确 a0/a1 与 A 的版本对应。上下文能够推断，但 C/B 在第一次使用时定义得更完整。
- coalescing 与 ACK 的核心“为什么”主要在讨论节才收拢。若读者在方法节追问“接收后就 ACK 为何不行”，需读到后文；B 把这一解释紧跟在协议规则后，局部衔接更好。
- 方法中故障处理集中在一个较长段落，读者要同时跟踪 duplicate、range、late message、disconnect 和 fallback。这里保留细节是有益的，但按发布前检查与历史失效分段会比删除细节更有效。

## B：技术层次清楚，对旧 coherent root 的定义最明确

**优点。** 2.1/2.2/2.3 将 target 语义、版本推进/失败、资源代价分开，适合定位具体约束。它在 ACK 规则之后立即说明 `“An acknowledgement on receipt would describe progress the renderer has not committed”`，因此无需读到讨论才理解后续 coalescing 的错误 base 风险。工作量由状态依赖推动，而不是由模块枚举推动。

评价定义多了一句 `“Old coherent roots remain acceptable while delivery proceeds.”`，特别有助于防止读者将一致性误读成“请求之后必须一直显示最新 target”。A/C 的方法例子也能得出这一点，B 则在指标定义旁直接说清。对 table 的 wire/preparation median、payload peak、二进制单位和 framing 说明完整。

**局部损失或可改进点。**

- 与 A/C 相比，具体两 tile 示例延迟到方法节；开篇的 coherent-view contract、coordination、coalescing 和 fallback 密度较高。前文对问题已正确描述，但初次进入时抽象负担更大，开篇结论没有因全文分节而消失。
- 原始 `draft.md` 明确 `“No compression was enabled.”`，B 全文未保留此条件；A/C 保留。它是传输量比较的有用实验条件，宜在共享 serialization/transport 的句子附近补回。当前并未声称启用压缩，属于条件遗漏而非相反陈述。
- 单读者一周期释放假设、fast-local 仅 sparse、单固定调度及无重复等限制集中到讨论末段。其中内存假设距离表格最远；读到 1.06 MiB 时，读者只知道排除元数据，尚不知道释放假设。将假设就近放在表注更利于即时正确解释。
- fallback 发生数在评价段，不能继承 sparse-path 收益的限制在讨论段；都在，但需要回读连接。可合并到功能证据段，无需增加更多免责声明。

## C：技术事实保持完整，公平基线突出，但有一处趋势语句需修

**优点。** `“Full-snapshot staging provides the strongest simple comparison because it already preserves root coherence.”` 很早就建立正确比较对象。方法连续解释 coalescing 为什么要 target 值、为什么不保证最小差分，以及 late packet / base check / fallback 的作用。独立的功能证据部分有助于把表内代价比较与 28 条功能 traces 分开；并明示没有 adaptive selector 评价，不把有条件的结果变成已验证选择策略。

功能段还保留 `“Coalescing generates target values once per coordinate, and range checks reject malformed tile IDs.”`，比 A/B 更显式保留 N5 中这两项检查。三稿都描述了对应机制；C 的覆盖表述更完整，但仍不等于新增实验。

**局部损失或可改进点。**

- `“Payload retention declines from FS's 2.00 MiB to SP's 1.06, 1.38, and 1.94 MiB as changes become denser.”` 容易被读成“越稠密，SP 保留载荷越低”。真实序列恰是 SP 随密度增大从 1.06 升至 1.94 MiB，相对 FS 的节省缩小。数值正确，但句子混合了“相对 FS 更少”和“随密度增大”的两个方向，是本轮最应优先修的局部语义风险。建议直说：SP 在三种模式都低于 2.00 MiB，但从 1.06 增至 1.94 MiB，优势随密度增大而收窄。
- 表注说明 binary units，却没有保留 N1 中 **wire bytes include protocol framing**。A/B 有这项说明；C 宜补回，以免将 wire 数字误当纯 tile payload。
- 64 个指针、4,096 个单元、四字节与总负载大小在简介即集中出现；理解问题暂不依赖这些数值。可以保留全部事实并移到方法，像 A/B 那样降低开篇来回切换概念与规格的负担。
- 方法中反复出现最后 coherent root、pending 不可见、显示可见旧版本等说明，分别服务于不同边界，但可更紧密地组织；不建议通过删掉 reader 不等待或远端不同时显示的限制来缩短篇幅。

## 对工作量、结果归因和读者负担的综合判断

三稿都把新增工作落实到四个依赖：指定且可验证的 base、基于 target 值的跨版本 coalescing、只对已经发布的 root 进行 ACK、历史或状态失效时退回 FS。28 条功能 traces 和两种失败变体说明这些规则为何值得验证，而没有以代码数量、bitset 或 packet 数量证明工作量。没有任何一稿将 28 条功能 traces 当作新的计时样本，也未将八条 fallback 的恢复代价伪造成表内稀疏收益。

相对原稿，三稿均更容易沿“错误画面 → 既有一致性基础 → 新增传输规则 → 合格基线下的代价 → 负例和范围”阅读。具体差异是：A 最容易从问题进入；B 的方法检索和 ACK 因果解释更就近；C 对公平基线与功能检查覆盖更显式。A 的 median 准备时间标注、B 的无压缩条件遗漏、C 的 framing 说明遗漏都属于可定位的口径损失；C 的 retained-payload 趋势句另外需要消除方向歧义。

这些差异支持局部取舍判断，尚不支持“某生成条件严格优于另一个”的结论。保留开篇阶段 **A 最容易进入** 的判断，但不把它自动扩大为全文整体胜者；三稿均有明确收益与局部代价。此报告结束于首次稿阶段，最终自修稿需在明确授权后另行评阅。
