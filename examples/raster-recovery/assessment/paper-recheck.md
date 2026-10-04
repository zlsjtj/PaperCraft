# 评后修复件针对性复验

**结论：本次指定的正文与排版问题均已在实际清稿中解决，可以作为修复后的 DEMO 文稿交付审阅。未发现本轮修改引入新的事实错误。** 这是一份已知问题驱动的模型复验，不是独立首稿、重新盲评或作者接受；原始匿名报告和首读判断保持冻结。

复验对象为 delivery-v2/manuscript_clean.docx、manuscript_text.md、clean-render/manuscript_clean.pdf 和全部 6 张页面图。事实参照 trial-evaluation/facts.json 与 trial-material/specification.md。未编辑稿件，未读取开发修改说明来代替产物检查。

## 修复是否落实

| 原问题 | 实际清稿证据 | 复验判断 |
|---|---|---|
| 摘要的 BS 收益缺少同场景配对 | p1：“In one two-cut schedule they save 49.0 ms over rows and 40.0 ms over appends”，并保留无中断 +60.0 ms 和十次切断 AR 更快 | 已解决。49/40 ms 对应 T9 的 2885−2836 与 2876−2836；正向收益及不利结果可在摘要一起理解。 |
| 正文缺确切切断日程 | p4 列出 T1–T4 全部时刻、T5 从 300 到 3000 ms 每 300 ms 一次，T6–T11 为 s 和 2s，s=500…1000 ms | 已解决。全部与 facts.trace_definitions 相符，无需外查即可恢复本次比较输入。 |
| 条件说明被排成 9 pt 粗体附注 | p4 的“Table 1 compares…”和“T6–T11 form…”是 11 pt Times New Roman 正体；已通过实际页面和 PDF 字体信息双重核对 | 已解决。时钟、相位和诊断范围恢复正文层级，没有以删减条件换取简洁。 |
| 表注声称表内保留完整日程 | p4 表注现为“Powered completion times (ms) and cut counts for all twelve constructed schedules” | 已解决。和实际 Trace/Cuts/RC/AR/BS 五列表一致；完整时刻由上方正文提供。 |
| 采用结论强于单配置证据 | p5 将“earns its place…”改为需要权衡的 intermediate choice，明确“In this configuration”，并写“It supplies no adoption threshold or general ranking…” | 已解决。具体 T7/T9/T11 获胜及 RC/AR 反例保留，结论不再暗示已经得到一般采用阈值。 |
| 公式与引导段分页 | 引导段、Equation 1 及后续解释均在 p4；DOCX 中存在原生数学对象 | 已解决。读者不必为核对公式定义翻页，公式语义仍为完整事件时长与部分事件耗时之和。 |

## 事实与文件一致性

DOCX 原生表格的 36 个时间值和切断次数均与 facts 一致。DOCX 与 manuscript_text.md 的正文/表格文字在空白规范化后相同；清稿含 1 个原生表格、1 个原生数学对象及 2 个嵌入图。这些是产物结构核对，不是写作效果评分。

完整 6 页可从标题读至结论与内部来源。没有发现文字遮挡、表格裁切或内容缺页。T0/T5/T10 负结果、T1 重采更少却不最快、payload-before-seal 的假设、连续前缀停止条件、旧 checkpoint 完成、+4 mm 坐标控制、仅八个剩余样本的范围、有限检查与真实硬件验证的区别均继续保留。修订没有把 DEMO 写成真实基准或已成立的外部原创性。

## 可以交付的范围

可交付为**已完成本轮编辑修复、等待作者审阅的 DEMO 清稿**。摘要现在先交代工程矛盾和配对收益，正文给出完整比较条件，采用结论与证据范围一致。本次复验没有替换原始匿名比较结论，也不应据此把评后选稿回写成匿名首轮胜者。

## 仍有局限

- T9/T10 反转仍用总时间、重采与事件相位作解释，正文尚未展示某一条具体事件账本分解；这是原评阅的可选深化项，不阻止本次编辑交付，也不能凭总数猜测反转阶段。
- p4 底部的第一段结果解释跨到 p5，49/40 ms 差值位于续页；没有丢失内容，摘要已完整给出差值，故属于轻微阅读连续性折中，不是未修复的公式分页问题。
- 本次未审阅黄色稿一致性或全部 SVG/PDF/PNG 图形版本关系；图形独立审阅、全套格式验收及作者接受仍应各自记录。没有真实设备性能、新颖性、普遍可靠性或人类阅读时间结论。
