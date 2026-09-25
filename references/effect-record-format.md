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
