# 编辑决定（独立试用）

## 写全文前的两个实际入口

### A — Holding Two Sample Readings Until Their Reference Interval Closes

A sample reading cannot be corrected from a future reference that has not yet arrived. Our controller keeps two readings private until a closing reference completes their interval, then exports both corrected values together. If either endpoint is missing, neither value is substituted from a neighboring group. This export rule makes reference bracketing usable in a scan controller, but its value depends on whether the saved acquisitions justify interpolation across changes in offset.

### B — Two-Well Reference Bracketing: Scheduled Scan Savings and a Step-Offset Limit

Measuring a reference before every sample already provides a strong response to changing offset. The remaining question is whether fewer reference acquisitions can preserve useful correction under specified changes. Bracketing two samples with shared reference endpoints reduces a scan from sixteen acquisitions to thirteen in this constructed fixture. The gain is conditional: the linear-drift example improves, whereas an offset step inside a group makes the bracketed result worse than the per-sample comparison.

## 选择及其代价

在首份全文前选择 B。它从强对照已有能力出发，让采集预算与偏移形态共同决定 R2 的用途。A 保留了必要的工程动作，却容易把未单独计时、没有独立新颖性证据的队列所有权误读为论文的主要增量。B 的代价是需要在方法中再解释“等闭合参考才导出”的具体困难；全文为此保留完整操作段。

## 冻结范围

- 原始材料只有 `../input.md` 和 `../task.md`；候选 skill 及所需参考是编辑方法来源，不提供本试用的实验事实。
- 正文保留 editorial DEMO 披露；所有结果均为 authored fixtures，不能称实测或部署验证。
- 完整结果表保持原单元格、顺序及 Markdown 原文。
- 先保存 `first.md`，其后只允许一轮自修并另存 `final.md`。不调用外部审阅者，不读取其他任务产物，不做新实验或联网。
- Markdown 文字与事实核对在本任务完成；Word 页面由父任务处理，本任务不宣称页面视觉验收。

## 本轮交付决定

完整首稿保存后完成一次自修，仅重排方法段并将摘要的 bracketing 关系写得更具体。首稿及终稿分别为 816、796 词（不含表格和 Markdown 标题标记，含题目、披露及表题）。最终保留 `final.md`；`self-review.md` 记录实际前后句及判断边界，`traceability.md` 记录正文事实落点，`loaded.json` 记录加载范围及 SHA-256。没有外部评语修复轮。
