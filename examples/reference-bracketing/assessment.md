# 新材料首稿与最终稿独立评阅

## 范围与结论

先只读两稿的标题、摘要和引言，已在读取原始材料前保存 `front-review.md`；随后仅读取本例的 `input.md`、`task.md`、`reviewer-only.md` 及 `output/first.md`、`output/final.md` 全文。未读取 skill、decision、自审、生成身份或其他产物，也未修改稿件。评阅包含原始表格和算术核对，不包含新实验。

两稿均将零散控制器描述组织成了明确、受证据限制的主线：以已经支持变化 offset 的 R1 为主要对照，考察两个样本共用前后参考的采集节省、组内插值失配，以及完整参考到齐才可导出的工程条件。最终稿改善主要在摘要一句和方法的因果衔接，未发现数值错误、关键负例遗漏或自修引入的实质退步。仍有小幅表述改进空间，且无法由提供的汇总数据重新推导所有误差值。

这是独立代理的模型辅助文本评阅，不是人类认可、实际科研验证或排版验收。该新例只有一个生成条件，不能据此判断优于普通生成、旧版或其他技能，也不能证明某种能力稳定迁移。

## 全部数值与记录范围核对

以原始材料逐项核对，另用只读脚本比较完整 Markdown 表格：两稿的表头、分隔行和 **9 条记录与 input.md 逐字符相同**。原始表格均完整保留，没有筛掉 R0、阶跃或较差结果。

| 核对对象 | 原始材料与两稿 | 评价 |
|---|---|---|
| 装置与数据含义 | 8 个编号样本井、1 个光学传感器；固定光学参考；任意 signal units；样本真值为作者设定且 evaluator 已知 | 没有引申浓度、温度、生物性质或独立硬件创新 |
| R0 采集数量 | 1 次 reference + 8 次 sample = 9 次 | 正确；两稿均解释只在扫描开始测一次参考 |
| R1 采集数量 | 8 次 reference + 8 次 sample = 16 次 | 正确；每个 sample 前有自己的参考 |
| R2 采集数量 | 8 个 sample 分成 4 组；共享相邻组端点产生 5 次 reference，共 13 次 | 正确；最终稿显式写出四组，属于由已有条件得出的算术，不是新实验 |
| 时长 | R0/R1/R2 为 90/160/130 ms | 与 9/16/13 次固定时长采集相容，均对应每次 10 ms 的安排；文稿正确限定为 scheduled scan completion，排除 file writing |
| 常数 offset | R0/R1/R2 均导出 8 个 sample，误差均 0.0；时长分别 90/160/130 ms | 正文明确 R0 最快且更简单，没有为了凸显 R2 隐藏它 |
| 线性漂移 | R0/R1/R2 均导出 8 个 sample，最大绝对误差分别 7.0/0.5/0.0 | 摘要、结果和表格一致；R2 对 R1 少 3 次采集、少 30 ms 的计算正确 |
| 组内 step | R0/R1/R2 均导出 8 个 sample，误差分别 8.0/1.0/4.0 | 两稿明确 R2 较 R1 误差更差，同时仍有较短 schedule，没有混淆误差与时长两个方向 |
| 功能 checklist | 独立 8 个 case，全都符合规定 export oracle | 未写成计时消融，也没有把 oracle 匹配扩展为部署正确性证明 |
| 缺参考记录 | 其中 2 个 case 只导出 6/8 个 sample | 均明确排除在完整 8-sample 误差表之外，不计作零误差；保留无恢复延迟结果的限制 |

篇幅也符合任务范围。按空白分词计、排除完整表格而保留标题、披露和小标题，首稿 822 词、最终稿 802 词；进一步排除标题、披露和表注后的正文分别为 750、730 词。两种口径均落在 650–850 词要求内。这里的词数用于核对长度，不代表人类阅读速度或质量分数。

**验证的实际边界：** 表值可以确认忠实于输入；采集次数和时长差可以核算。但输入没有提供逐次原始读数、offset 数学函数、具体 step 时点及完整数字时间戳，因而不能独立重算 7.0、0.5、4.0 等误差。两稿没有伪称完成此类复现。这个局限来自本例资料粒度，不能通过润色补成真实测量或未经提供的新数据。

## 科学主张与负结果

**对照选择合理。** 两稿开篇先承认 per-sample reference 已处理既定变化 offset，结果又明说 `“R0's errors of 7.0 under drift and 8.0 under the step also show why it is not the decisive changing-offset comparison.”` R0 提供常数情形的简单选项；R1 才是变化 offset 下的主要比较对象。没有仅靠击败较弱 R0 构造收益。

**继承和新增没有混淆。** reference subtraction、scan order、reference well、firmware 均是已有设施；`“Interpolation is existing arithmetic, not a new estimator.”` 明确排除了插值算法新颖性主张。成稿将本例新增工作的重点放在端点共享的安排、组内读数暂存与导出资格，而不是把每个 queue、setting 和 check 都写成贡献。

**误差收益限定正确。** 摘要虽然突出线性漂移下零误差，随即给出 step 的 4.0 对 1.0；方法解释两端点不能重建组内 step，讨论以 `“Delaying export protects the bracket's completeness without resolving its step sensitivity.”` 再次区分流程完整性与信号重建能力。没有将“数据到齐”误写成“物理漂移一定被校正”。

**计时与因果边界明确。** `“the authored timings follow the prescribed schedule and are not independent performance measurements”` 使 130 对 160 ms 的意义清楚：它是给定采集时长和采集次数的安排结果。queue ownership 没有独立计时，功能 checklist 没有成为性能因果证据。文稿未声称算法、硬件或队列实现的独立加速。

**未覆盖事项没有消失。** 无 repeats、confidence intervals、noise tests、variable-duration scans、stochastic missing-value statistics，以及缺少 prior-art survey、独立硬件创新和部署优势证据，均保留。披露明确是 authored editorial DEMO，不可当成真实研究依据。

## 工程决定是否解释了必要性

| 决定 | 文稿给出的原因及其证据 | 评价 |
|---|---|---|
| 相邻组共享端点 | 同一扫描中，一个 closing reference 也作为下一组 opening reference；因此四组只需五次 reference | 采集节省的来源可追踪，未归因于更快电子学或改变扫描顺序 |
| 不跨扫描复用尾端参考 | 两稿明确一个 scan 的尾端参考不用于下一 scan | 保留了原始安排的边界，没有暗中进一步减少计数 |
| 在 acquisition-start 时间戳插值 | 两稿说明时间戳含义和所有 acquisition 的相同规定时长 | 未将 acquisition end 或可变采集时间混入条件 |
| 组内两个 sample 私有暂存 | 样本到达时 closing reference 尚未得到；最终稿明确不导出 interim corrected values | 暂存与完整区间的依赖明确，不是空泛队列清单 |
| 缺任一 reference 判 unavailable | 无有效完整区间，不以前一组 reference 填补 | 避免捏造 correction；与六样本功能记录的排除规则一致 |
| queue ownership 阻止不完整 pair 导出 | 8-case export oracle 检查 first/last groups、shared endpoint identity、repeated packets、timestamp rejection、missing ending reference | 功能覆盖范围被保留，同时没有宣称独立性能效果或无遗漏证明 |

这一部分的实际收益在于，输入的 `“a lot of settings and checks”` 变成了由参考区间语义驱动的少数必要决定。任务没有提供现成贡献句；从成稿可观察到它自行组织出了采集预算、offset 形状与完整导出条件的联系。该观察针对最终文本，不认证其内部生成过程，也不外推为稳定能力。

## 首稿到最终稿：改善、保留及不足

**改善一：摘要降低术语负担。** 首稿的 `“bracketing two samples with shared reference endpoints”` 改成两次 sample readings 的前后 reference、相邻组共享 endpoint。首读时更容易建立顺序，不需要先理解 bracketing 的术语含义。

**改善二：方法先给操作顺序，再给计数。** 最终稿用 `“An R2 group reads an opening reference, two samples, then a closing reference.”` 起始，随后说明 closing 同时打开下一组，再得出四组、五次参考、十三次 acquisition。首稿事实相同，但数量推导和前后端点的联系较分散。最终排列能更直接回答“13 次从哪里来”。

**改善三：私有暂存的触发条件更具体。** 最终稿 `“When either sample arrives, its closing reference is still unavailable. R2 therefore stores both readings privately and exports no interim corrected values.”` 比首稿 `“Its use connects each sample correction to both endpoints”` 更贴近实际到达顺序。缺参考则 unavailable 的规则紧跟其后，入口提出的 export policy 在方法中得到承接。

**保留的能力和无退步项。** 结果、负例、表格、功能记录和限制保持完整；最终稿变短没有删去关键条件。没有发现自修引入的数值、计数或科学解释错误。自修改善集中于可读性和解释顺序，不是新增实验、原创性证明或证据强度提升。

**仍可改进的局部点：**

- 标题 `“Two-Well Reference Bracketing”` 可能被快速读成“两口 reference wells”，而实际是两个 sample readings 组成一组、既有 reference well 被重复读取。摘要和方法能消除歧义，因此不是正文的装置事实错误；标题若改用 “Bracketing Pairs of Sample Readings” 一类表达，会更准确指向成组操作。
- 摘要 `“already addresses changing additive offset”` 没有限定 stipulated fixtures；引言才补上这一范围。后文给出了 R1 的非零误差，因此没有承诺普遍精确消除 offset，但摘要若写成“addresses the stipulated changing-offset cases”会减少泛化空间。
- 输入未给连续 offset 函数或原始读数，文稿只可说明插值条件与报告固定误差，不能让读者从源数据独立复算每项结果。若未来将其用于真实论文，需要实际数据和实验设计；本轮编辑不应填造这些缺口。
- 两稿没有定义所有可能坏包或所有 missing-reference 排列下的行为证明；8 个 functional cases 只是提供的有限 checklist。当前文本没有夸大，不能因为写得顺畅就将有限覆盖读成协议完备性。

## 评价范围内的最终判断

这一个新例满足基础事实保真、公平对照、负结果保留和工程必要性说明。最终稿相对首稿有具体且有限的阅读改善，主要在方法顺序及导出条件的解释，未发现新增实质退步。它仍是合成材料上的一次写作迁移观察，既不是“论文已达到真实发表要求”，也不足以给出不同技能或生成条件之间的优劣结论。
