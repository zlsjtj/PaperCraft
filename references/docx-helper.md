# 可执行 Word 辅助工具

`scripts/review_docx.py` 负责落实已审定文字和变化映射，**不自动发现创新、不校验实验真实性**。模型先读材料、填写证据与修订 manifest，再运行工具。生成两份真实 Word 以及 JSON 映射，清稿可选。

## 使用

使用当前宿主可用的 Python。若宿主另有文档技能，遵循它的实际操作要求；本包的受控修改工具本身不依赖该技能：

```text
python scripts/review_docx.py inspect input.docx --out inventory.json
python scripts/review_docx.py build input.docx manifest.json new-output-dir --clean
python scripts/review_docx.py verify input.docx new-output-dir/input_包装审阅版.docx
```

`inspect` 只读 Word。段落 ID 为 document.xml 中直接正文段落 P0001 起；表内段落不计。清稿没有本轮黄标，但保留输入文件的已有高亮。

### 按能力清单选择操作

`editable` / `reason` 保留旧格式兼容：只表示该段能否通过**整段操作的局部结构检查**，不能单独当成可执行结论。`editable: false` 不等于段内没有可改文字；`editable: true` 也可能被文档中的历史修订阻断。

| 清单字段 | 如何使用 |
|---|---|
| `document_blockers` | 文档级阻断、受影响操作及 XML 位置。历史修订阻断整段操作；格式异常的复杂域阻断两条编辑路径 |
| `whole_paragraph.available` / `operations` / `blocked_by` | 整段 replace 等操作在当前文档中是否可用，包含局部与文档级检查 |
| `ordinary_spans.groups` | 连续且格式相同的普通 run 组，给出原文、文字/格式哈希、run 的 XML 位置、段内子节点序号和数量 |
| 组内 `eligible` | 该组由现有 span 编辑器认可的普通文字组成；仍须检查唯一匹配和段落阻断 |
| 组内 `replaceable_as_whole_group` / `operation` | 整个组的文字能否直接作为唯一 `before`；为真时 `operation` 给出 kind、target 和 before，补充 after 后放入 manifest 的 spans |
| `protected_content` / `protected_objects` | 原样保留的对象、位置、文字和原因，包括域缓存、公式、链接、旧高亮及修订边界；不从显示文字推断可编辑 |
| 段级 `operations` / `recommended_route` | 当前段的可用操作与文字修改建议。无安全路线时推荐值为 null，不能改用整段重建 |

候选组与 `replace_span` 共用 run 资格、同格式分组、精确匹配和域结构判定。组 ID 与 XML 路径用于定位，不是新 manifest target；target 仍用 P 段号，expect 用完整原段文字。斜体等普通样式可以形成独立组，但不能跨格式边界拼接；原有高亮和历史修订内文字仍不可改。清单不替编辑者生成科学结论或 author confirmation。

若任一目标需要 `replace_span`，**同一份计划里的普通段落也用 `replace_span`**，从它自己的 eligible 组选择 before；同段多处修改归入一个 spans 数组。不能把各段推荐值直接拼成混有 replace 与 replace_span 的计划。`insert_after`、delete、move_after、format 不可放入 span 计划；确实可用且已获当前任务授权时，单独构建，再对确切输出重新 inspect，使用新的父哈希与段号。`plan_selection` 也记录此约束。

字段字符缺失/未知、域未闭合、孤立字段指令等异常由只读 inspect 返回 BLOCKED 和 XML 位置；build 用同一判定拒绝，保留输入且不发布部分产物。清单描述本工具的结构能力；表内文字、公式/域结果重写、刷新域、跨段片段和接受历史修订仍列在 `unsupported_operations`，需要另行采用合适工具处理。

## 修改清单（Manifest）

采用 [完整字段示例](../templates/revision-manifest.json)。`input_sha256` 必须是实际原稿；`scope` 为 full/local/continue。仅诊断用 inspect，不调用 build。输出目录必须未存在，每次续改用新目录、重新 inspect 和新父哈希。

`operations` 每项：唯一 id；kind；target 段落 ID；与原段完全相同的 expect；purpose；可定位的 evidence；Boolean confirm。

| kind | 额外参数 | 行为 |
|---|---|---|
| replace_span | spans [{before, after}] | 精确替换复杂段落中的普通文字，保留周围对象与历史修订；新文字黄标 |
| replace | text | 整段改写，审阅稿全段黄标，保持段落和首 run 格式 |
| insert_after | text | 在 target 后插入，继承段落格式，黄标 |
| delete | 无 | 删除原段，完整原文进入映射/报告 |
| move_after | after 原段 ID | 原段移动；不冒充黄标可表达删除/移动 |
| format | format 对象 | 只支持 space_after_pt 0–72 或 keep_next true/false，记录前后属性 |

同一原段只允许一次操作，避免先改后删导致映射含糊；需要多项变化时用格式感知流程。整段操作的目标含公式、图、域、超链接、书签、混合 run 格式或已有高亮时会拒绝；表内文不属于可寻址目标；文档遇到历史原生修订也会拒绝整段操作。受保护对象之间的普通文字可按能力清单改用 replace_span，它不接受或删除历史修订；跨保护边界的匹配仍拒绝。

未改图片/表/公式/脚注/引用及其他 ZIP 部件保留。重写普通文字中的手工引文编号仍需编辑核对。外链更新、字体替换、图表重绘和原生 Track Changes 不由该脚本实现。可以通过真实文档工具完成并做另行变更记录。

对复杂对象继续按 [长稿与复杂 Word](complex-word.md) 处理；本版增加受保护对象之间的文字片段路径，保留整段替换的拒绝规则。新增只读 `audit_preservation.py` 可检查精细修改后的原生数学内容、表格内容与明确保护段。审阅映射的重要变更仍需写明原问题、改善内容、证据和适用边界；旧 manifest 的 purpose/evidence 保留兼容，不要求为了填字段改动已清楚的原文。

## 输出与检查范围

`*_包装审阅版.docx`、`*_诊断报告.docx`、可选 `*_清洁候选稿.docx`、`change-map.json`。全文报告保留贡献与证据检查。`scope: local` 自动生成基线、实际片段、理由、受影响检查和剩余问题的简短记录，不强制标题备选、贡献表或图状态。续改可显式给 `report_scope: local`；旧全文清单保持兼容。

`verify` 只证实 ZIP 与受保护对象；它不是全文科学审查或变化完整性证明。构建路径对实际补丁生成映射；检查每项黄标与目标文本、删除原文、移动位置和格式属性。生成时 `visual_review` 必为 NOT_RUN，作者认可 false，投稿未执行。之后用真实渲染器生成最终页面，逐页检查并写 `visual-review.json`（路径/哈希、页数、工具、检查者、问题和结果）。记录本地编辑检查，不假称真实同行评审。

报告从模板字段生成，无实质内容的 manifest 不算修订完成。任务实际需要而工具不支持的编辑，用成熟文档工作流继续完成，不让脚本限制替代用户目标。
