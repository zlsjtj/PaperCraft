# 将编辑决定安全写回复杂 Word

这个例子只验证入稿路径，不是研究成果。原文同时含原生公式、斜体、链接、表格和历史插入标记。目标是在公式之后的普通文字边界拆段，再修改普通文字，保留其他结构。

```powershell
python examples/authored-edits/build_fixture.py --out output/source
python scripts/apply_authored_edits.py --source output/source/input.docx --edits output/source/edits.json --skill . --out output/revised
```

`output/revised/clean.docx`、`review.docx` 与 `build.json` 分别是清稿、黄色稿和节点/文字保护记录。已有原生修订保留，不被自动接受。脚本拒绝重复定位、公式内部切分、含字段或原生修订段的拆分，保留失败，不能换成整段纯文本绕过保护。

补丁字段包括 `paragraph_id`、`operation`、`before`、`after`、`reason`、`source`；`split_after` 是唯一普通文本标记的数组，标记必须在修改后的段落中存在。无文字改写的拆段用相同的 before/after。原段号来自 `review_docx.py inspect`，不是 Word 页码。

连续段落被非语义字体提示拆碎时，先查 inspect 的 `authored_prose_diff`，再用同一 CLI 交付 `operation: "rewrite_prose_preserving_runs"`。它要求准确完整 before/after 和 source_sha256，按文字差异保留原 run，限于普通 ASCII 西文中显式同字体的 hint 差异；不能跨真实样式、保护节点或历史修订。此操作不与同段 span/split 混用。可执行回归入口为 `python -B -m unittest discover -s tests -p test_authored_run_rewrite.py -v`，包括输入不变、黄标范围、重复短语及语义格式/域/书签/公式/分页边界拒绝。详见[受控接续](../../references/complex-word.md)。

该适配器先在一份含83个原生公式的长稿上用于17项文字或段落编辑，逐项比较数学XML、表格、声明、引用和嵌图；那份未发表稿不收入仓库。这里的公开输入用于从源码重建同一路径。保护通过不说明改写有说服力，实际分页必须另用 `render_review.py` 查看。
