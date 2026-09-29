# 本轮全文编辑记录

交付对象是已有 heat-story DEMO 的继续开发。全部案例、时间、误差、残差与实现结果均为给定构造材料；这不是未见长文测试、真实实验或审稿人认可。本轮只写当前 story 输出目录，未改原仓库、图源或图像。

## 实际交付与改动价值

`before.md` 是本轮上一版的原始字节副本；`first_draft.md` 保留首份完整稿；`manuscript.md` 是其后一次自审修复的最终稿。按空白分词，前版 3253、初稿 3464、最终 3220，包含表格。减幅本身不作为效果证据。

这次改动主要让读者更早作出两个判断：快照归属为何是有必要的工作，以及增加这项工作后何时值得用 G。摘要把组级指数计算、快照读取和 50% 数组预留一起放到设计之后；引言沿“邻组刷新可能替换错误参考状态”解释两端快照为什么必须跟随面所有者。结果入口直接指出 boundary ramp 与 moving source 是 G 有区分价值的两例，同时把 slow plate 留给更便宜的 P4，把两项负结果留给 V。没有把一般工程步骤拆成三项创新。

## 逐节判断与取舍

| 范围 | 原稿判断 | 本轮动作与理由 |
|---|---|---|
| 标题 | 已有具体对象、具体关系与应用领域；不是空泛“框架”标题 | 原样保留。改成效率主张反而超出现有证据 |
| 摘要 | 结果基本准确，但 guard 的实际工作读得稍晚，P4 的胜出条件不够明确 | 前置指数测试、快照读取与内存代价；说明P4在slow plate是更便宜的合格选择 |
| 引言 | 动机与边界清楚；方法预告仍偏“比较有效”的概括 | 改成邻组刷新改变快照的具体困难；末段用强基线交代为什么比较 |
| §2 | 六个公式中的模型与row-sum部分已经清楚，守恒与准确性区分必要 | 全节原样保留，不为显示改稿而替换术语 |
| §3.1 | 所有权解释在引言、正文、图注后重复；成本分散 | 先读A保留/B刷新，再给归属规则与界；删除后方重复段；复用选择旁交代热点触发整组、测试工作和存储 |
| §3.2 | 顺序完整，但入口像执行清单 | 先区分复用许可与提交许可；用“减小dt能修row sum而不能修同温度的指数求值”组织abort/retry；保留全部退出、八次减半、缓存作废和提交规则 |
| §3.3 | 算术例与R1/R2/R3边界已经具体 | 原样保留；0.5 s终点与控制描述非日志均在正文 |
| §4 | 首段先堆配置，读者还不知道V/P4分别回答什么 | 先给两个对照职责，再给匹配条件；网格、源和物理参数完整留在紧接段。计时、误差、能量残差与内存明细原样保留 |
| §5 | 三段数值解释已较好；开头再次给读图规则与DEMO提醒 | 开头改成有条件的采用判断；其后三个主结果段与全部表格原样保留；扫参增加一句承接 |
| §6—7 | 边界全面，但结论停在泛泛的条件价值 | 缺口集中保留；结论具体交代G/P4/V各自的合适情形，并回扣一致参考状态 |

## 三组实际前后效果

**机制段，从重复解释到一次操作。**

前：“A face crossing a group boundary explains why ownership matters. Its coefficient was evaluated using both endpoint temperatures at the owner's refresh. Updating the neighboring group's coefficients must not overwrite either associated snapshot…”

后：“In Figure 1, A retains its coefficient while B refreshes. The coefficient still depends on both temperatures at A's refresh, including the endpoint in B.” 后面紧接索引顺序、所有权与快照counter规则。原先图注后的重复段已删除，必要定义没有移走。读者先看到要保护哪个旧状态，再读存储规则。

**结果入口，从读图说明到决定。**

前：“Figure 2 brings time and final error together: a faster method is useful here only if it also meets the stated error limit.”

后：“G's useful cases are the boundary ramp and moving source: it saves time over V where P4 fails the error limit. Figure 2 places these cases beside P4's qualifying slow-plate result and G's two timing losses.” 原来的三个完整数值段继续紧随图后，首段不再重复其每个数值。

**控制段，从状态清单到规则依据。**

前：“Every selected coefficient must be finite and strictly positive. Exponential overflow or underflow to zero exits with INVALID_COEFFICIENT; halving dt cannot repair a constitutive evaluation at unchanged old temperatures.”

后：“The reason for separating abort from retry is that reducing dt can repair an excessive diffusive row sum but cannot repair a constitutive evaluation at unchanged old temperatures.” 后文完整给正有限系数、INVALID_COEFFICIENT、invalid-input不重试、0.95阈值及八次减半。新增的是这些现有规则的关系，不是新的故障实验。

## 唯一一轮自审

初稿为加强段落连接而重复了比较目的，增加211词。自审发现§5首段把三组结论完整重述、§4入口又重讲成本问题，遂压缩这些过渡，同时缩短摘要、引言与结论中没有独有事实的连接语。最终相对前版少33词。`self_review_once.json`保留10处初稿→最终的确切文本，`changes_first_draft.json`保留15处前版→初稿记录，`before_after.diff`给最终全文差异。没有第二轮自审改稿或外部意见后倒写首稿。

## 图文与验收范围

已实际查看两张选中PNG。图1可继续承担“B刷新不能改A的两端快照”这一个关系，正文改为直接引用A/B操作；图2已将时间、精度不通过标记与慢板成本拆分放在同一路径，保留。两图内容、图注与figures.json未改动，无需父任务改图注字符串即可嵌入。

六个Equation行逐字符且顺序一致；两表24个数据行、表头、行序均与前版一致，并将每个数据单元直接与两份原CSV核对通过。该检查只证明内容保留，不证明构造数据是真实数据。必要内容均保留正文，无附录转移。

本轮属于编辑者自审；Word/PDF页面、独立评阅与作者接受由父任务处理，不能以此记录冒充已通过。输入哈希见`loaded_sources.sha256.json`，在本轮输出冻结时计算；输出哈希见`output_hashes.json`。
