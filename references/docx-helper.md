# 可执行 Word 辅助工具

`scripts/review_docx.py` 负责落实已审定文字和变化映射，**不自动发现创新、不校验实验真实性**。模型先读材料、填写证据与修订 manifest，再运行工具。生成两份真实 Word 以及 JSON 映射，清稿可选。

## 使用

在已加载 documents 技能并完成其本次作者操作标记后，用宿主提供的 Python：

```text
python scripts/review_docx.py inspect input.docx --out inventory.json
python scripts/review_docx.py build input.docx manifest.json new-output-dir --clean
python scripts/review_docx.py verify input.docx new-output-dir/input_包装审阅版.docx
```

`inspect` 只读 Word。段落 ID 为 document.xml 中直接正文段落 P0001 起；表内段落不计。清稿没有本轮黄标，但保留输入文件的已有高亮。

## 修改清单（Manifest）

采用 [完整字段示例](../templates/revision-manifest.json)。`input_sha256` 必须是实际原稿；`scope` 为 full/local/continue。仅诊断用 inspect，不调用 build。输出目录必须未存在，每次续改用新目录、重新 inspect 和新父哈希。

`operations` 每项：唯一 id；kind；target 段落 ID；与原段完全相同的 expect；purpose；可定位的 evidence；Boolean confirm。

| kind | 额外参数 | 行为 |
|---|---|---|
| replace | text | 整段改写，审阅稿全段黄标，保持段落和首 run 格式 |
| insert_after | text | 在 target 后插入，继承段落格式，黄标 |
| delete | 无 | 删除原段，完整原文进入映射/报告 |
| move_after | after 原段 ID | 原段移动；不冒充黄标可表达删除/移动 |
| format | format 对象 | 只支持 space_after_pt 0–72 或 keep_next true/false，记录前后属性 |

同一原段只允许一次操作，避免先改后删导致映射含糊；需要多项变化时用格式感知流程。公式、图、表内文、域、超链接、书签、混合 run 格式、已有黄标的目标会拒绝；存在未处理的原生修订时整次 build 拒绝。拒绝不表示论文不能改，只表示需 documents 的更精细路径，不得绕过保护再称无损。

未改图片/表/公式/脚注/引用及其他 ZIP 部件保留。重写普通文字中的手工引文编号仍需编辑核对。外链更新、字体替换、图表重绘和原生 Track Changes 不由该脚本实现。可以通过真实文档工具完成并做另行变更记录。

对复杂对象继续按 [长稿与复杂 Word](complex-word.md) 处理；本版没有放宽 helper 的拒绝规则。新增只读 `audit_preservation.py` 可检查精细修改后的原生数学内容、表格内容与明确保护段。审阅映射的重要变更仍需写明原问题、改善内容、证据和适用边界；旧 manifest 的 purpose/evidence 保留兼容，不要求为了填字段改动已清楚的原文。

## 输出与检查范围

`*_包装审阅版.docx`、`*_诊断报告.docx`、可选 `*_清洁候选稿.docx`、`change-map.json`。报告含中文摘要、标题候选、三维前后对照、证据表、六维度、图状态、前后文与定位、负结果、作者事项和检查状态。

`verify` 只证实 ZIP 与受保护对象；它不是全文科学审查或变化完整性证明。构建路径对实际补丁生成映射；检查每项黄标与目标文本、删除原文、移动位置和格式属性。生成时 `visual_review` 必为 NOT_RUN，作者认可 false，投稿未执行。之后用真实渲染器生成最终页面，逐页检查并写 `visual-review.json`（路径/哈希、页数、工具、检查者、问题和结果）。记录本地编辑检查，不假称真实同行评审。

报告从模板字段生成，无实质内容的 manifest 不算修订完成。任务实际需要而工具不支持的编辑，用成熟文档工作流继续完成，不让脚本限制替代用户目标。
