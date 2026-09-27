# 更短却失真的候选如何回退

这是构造的记录格式示例，不是读者研究。原文只支持节点计算次数减少，候选却写成运行更快。字少了，科学含义退步了，所以记录为 mixed，分别记录两维观察并回退到基线。

```powershell
python examples/effect-tradeoff/build.py --out test-output/tradeoff
python scripts/audit_effect_record.py test-output/tradeoff/record.json --out test-output/tradeoff-audit.json
```

审核通过只代表字段完整、文件与哈希相符；不会自动确认“更容易理解”。旧 schema 1 记录仍可读取。
