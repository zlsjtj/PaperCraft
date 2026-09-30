# 反馈后交付修复

本文件记录匿名全文反馈后的定点修复，不属于首次生成或自主编辑胜出。基线为 final.md，修复稿另存 delivery.md；first.md、final.md、decision.md、loaded.json 均保持原有内容。没有重写标题、摘要、容量例子、章节组织或结果解释主线，也没有新增实现、实验、测量或其他科研操作。

四处修复均由原材料 implementation_notes.md 支持：

| 修复 | 交付稿落点 | 原始依据 |
|---|---|---|
| 补全空环初始化 | 方法中区分非空环的 hand 前插入与空环插入；后者将 hand 初始化到新对象。 | Shared state and scope，第 18–20 行明确空环插入初始化 hand。 |
| 明确前景扫描顺序 | 明写先检查 hand 所指对象，再推进 hand，然后依所检查的位清位或记录受害对象。 | Foreground procedure，第 24–27 行。 |
| 纠正维护操作对象 | 将含混的 “clears referenced objects” 改为清除置位的 reference bit 并推进；位清零时才推进并逐出对象，保留目标和额度停止条件。 | Maintenance for the reserve variants，第 59–65 行。 |
| 限定结果归因 | 结果节新增一段：Cap64 的前景额度为 64，Reserve 为 48，另有至多 16 次维护，因此比较完整预算拆分与预留组合，不能单独隔离维护作用。 | Five local policy IDs，第 44–50 行；Counters and limits，第 74–77 行。 |

原 1 MiB / 4 KiB / 256 个不同受害对象的条件例子、所有 DEMO 声明、负结果、引用和 20 行 CSV 绑定保持。delivery.md 约 1478 词，计数口径沿用 loaded.json：含标题、小标题和 DEMO 声明，排除表题、表绑定及来源。表格仍由主代理按 CSV_TABLE_BINDING 确定性插入。

基线 final.md SHA256：`e75ee63e889c0b102d0c5123a4d43ea0c7b079fb3469afb5a7b344720a8e7c29`。

修复稿 delivery.md SHA256：`51f907027337b352d8dd64fb70fd9f1db3570546273358158868b528455afbb2`。

此处核对仅确认文字与规范对应，不把规范要求写成已验证的状态不变量、并发安全或实际性能。本稿尚未获得作者接受。
