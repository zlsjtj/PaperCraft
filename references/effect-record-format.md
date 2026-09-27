# 可选的产物效果记录

多文件修订需要机器核对索引时使用，实际判断仍写入文字和视觉审阅。原有变化映射格式不变。

```json
{
  "schema_version": 1,
  "reviewer": "审阅者及实际阅读范围",
  "artifacts": [{"id": "clean", "path": "paper/clean.docx", "sha256": "文件的实际 SHA-256"}],
  "requirements": [{
    "id": "R1",
    "requested_effect": "用户要求的改善",
    "baseline_observation": "原稿中可定位的问题",
    "candidate_observation": "改后读者能够解释的内容",
    "assessment": "partial",
    "evidence": [{"artifact": "clean", "locator": "章节及短引文"}],
    "remaining": ["仍未解决的具体问题"]
  }]
}
```

路径相对于记录文件。`assessment` 可取 `improved`、`equivalent`、`partial`、`unmet`、`pending`；未解决状态必须说明残留问题。来源、审阅和改动文件也可作为产物。

运行 `python scripts/audit_effect_record.py effect.json --out new-audit.json`。工具检查文件与哈希，不判断定位是否有科学意义、观察是否真实或是否满足审美。有效记录也可以记录未达标要求；`overall_status` 保持 `REVIEW_REQUIRED`。已有输出会被拒绝。

## 改善与退步并存

旧 schema_version 1 记录仍按原字段处理，不推断其历史决策。新比较用 schema_version 2：assessment 可以是 regressed（退步）或 mixed（不同维度得失并存）。mixed 必须在 dimensions 中分别记录 improved 和 regressed，各带原观察、候选观察和文件位置；不要把误读增加藏进 partial。

每项要求增加 decision：action 为 keep_candidate、keep_baseline、revise、rollback 或 defer；reason 解释取舍，chosen_artifact 绑定当前保留的确切文件。rollback 另给 rollback_to，必须指向相同的已绑定旧产物；这只是记录决定，不自动执行文件回滚。regressed/mixed 还需 tradeoff 说明得失。未决问题继续放 remaining。

完整的可运行小例见 `examples/effect-tradeoff/build.py`。字段齐全或哈希一致只能证明记录对应文件，不能证明“更好读”真实、选择合理或作者同意。语义或科学误读不能靠把 decision 写成 keep_candidate 就变成通过。
