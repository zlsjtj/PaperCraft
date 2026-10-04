# PaperCraft 进阶使用与验证

[返回首页](../README.md)

这里收录依赖、脚本命令和检查方法。命令从仓库根目录运行；输出目录应为新目录。先通过宿主模型完成写作或构图，再用这些工具执行受控修改和导出。

## 工具与依赖

阅读、判断和改写由宿主模型执行。脚本负责定位、受控写入和检查，不会自行证明创新性。

在自己选择的 Python 环境中安装依赖：

```powershell
python -m pip install -r requirements.txt
python scripts/check_dependencies.py . --require docx --require preservation --out runtime.json
python scripts/review_docx.py inspect manuscript.docx --out inventory.json
```

简单正文可按照 [清单格式](../references/docx-helper.md) 编写补丁，再生成候选：

```powershell
python scripts/review_docx.py build manuscript.docx revision.json output --clean
python scripts/audit_preservation.py manuscript.docx output/manuscript_清洁候选稿.docx --out protection.json
```

输出目录应为新目录。含公式、域、交叉引用和混合格式的段落，其普通文字可用 replace_span；完整样例见[复杂 Word 流程](../references/complex-word.md)。已完成整段写作但普通文字分成许多 run 时，可用 `apply_authored_edits.py` 的 `rewrite_prose_preserving_runs` 接续；示例和拒绝边界见复杂 Word 流程。整段替换仍严格保护这些对象。PDF 和逐页图片还需要宿主的 documents 技能、可用文档渲染器与 Poppler；这些不随本仓库打包，详细说明见[依赖](../references/dependencies.md)。

新版补充[选择规则复核与定范围审阅](../references/method-transfer-audit.md)：检查训练配置如何映射到测试输入，并通过 `make_review_packet.py` 只提供明确选定的段落和图片。生成材料不等于完成独立审阅。

## 这次怎样判断是否改得更好

先看实际阅读阻碍，再决定改哪里。入口要分清主贡献、支撑、证据和边界；方法要让具体困难先变得可见，实验要说明每个比较在区分什么。必要推导和参数完整留在论文内，不把“简洁”变成删掉证据。

[论证修复](../references/argument-repair.md)负责连接具体困难、必要决定和证据。全文检查各节是否推进中心判断；已有清楚的内容可以保留，不以每段改写或篇幅增加证明效果。

审阅用实际前后稿回答：读者先看见什么，重要工作为何必要，哪里仍需往返查找。没有真实读者时明确称模型辅助评估。词数、答案齐全和工具通过不证明整篇好读；局部修改也不能冒充全文修订。

## 示例与检查

当前统一技术入口：

```powershell
python tests/run_all_tests.py --out test-output/current
```

它检查全库Python语法、旧回归、自动发现的单元测试和复杂Word示例的源码生成/build/verify路径。逐组报告失败、缺依赖和跳过，不能把这些状态合并成全部通过。输出不包括页面视觉验收或论文表达效果；这两项要另看精确产物。下面的旧单组命令继续有效，适合只复验受影响部分。

[检查点流水线示例](../references/checkpoint-demo/input.md)提供原文、限定证据、英文改稿和中文改动记录。数据是教学构造值，不能作为研究结果引用。其他[完整示例](../references/worked-examples.md)展示贡献、工程段和结果段的修改理由。

```powershell
python tests/run_tests.py --work-dir test-output/basic
python tests/run_preservation_tests.py --work-dir test-output/protection
python tests/run_integration_tests.py --out test-output/integration
python tests/run_effect_record_tests.py --out test-output/effect
python tests/run_review_packet_tests.py --out test-output/reading
python tests/run_representation_tests.py --out test-output/representations
```

再次执行时换用新的输出目录。本轮实际运行范围和产出审阅分别见[当前记录](../tests/current-validation.md)，旧结果保留在[历史验收](../tests/acceptance-results.md)。脚本通过不能作为写作效果的替代证据。

## 文件与发布范围

`SKILL.md` 是入口，`references/` 是具体方法，`templates/` 是工作记录，`scripts/` 和 `tests/` 是可执行工具及测试。

公开版保留当前功能代码，使用中文说明和匿名教学案例。私人稿件、未公开测量记录、本机路径、代理会话记录和历次生成缓存留在本地归档。英文论文示例、命令参数和第三方专有名称保留原文。来源见[来源说明](../references/video-source-notes.md)，许可状态见 [LICENSE.md](licensing.md)。

包装不能补出不存在的研究贡献，也不能保证期刊初审。已经表达清楚的段落可以保留；缺实验、缺对照和缺来源应明确记录。

历史试用在 Git 历史和版本验收中保留，不能代替当前版本验证。本轮区分首次完整稿、自主复读、外部评语后的开发修改，以及冻结后换材料再生成；共同排版工具的修复不记作某一生成条件的优势。

新增可执行示例：[复杂 Word 局部修改](../examples/complex-word/README.md)、[明确退步与回退](../examples/effect-tradeoff/README.md)、[三组真实改写对照](../examples/three-way-reading-demo/README.md)。

科研图示例的重建依赖单独列在示例目录。可用 `python -m pip install -r examples/visual-editorial/requirements.txt` 安装 Python 部分，另提供本机字体和 Poppler；生成 Word 后仍需实际渲染和检查页面。

[箱角解锁新材料试用](../examples/bin-latch/README.md)保存普通提示、旧技能、新技能的首次产物与匿名比较。新版的状态对照更直接，但并非全面胜出；反馈后修复单独记录。

[锁止时序新材料案例](../examples/clamp-timing/README.md)提供原始材料、清稿与黄色审阅稿、可编辑图源和真实比较得失。该案例没有预写贡献答案，也没有把新版包装成全面胜者。
