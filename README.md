# PaperCraft｜论文叙事与精修

PaperCraft 用于修改已有研究论文：把贡献讲清楚，把必要的工程工作写充分，让正文、图表和证据相互对应。它关注创新点包装、工作量包装、图文呈现和透明审阅，修改以已有材料为依据。

当前版本 **2.8.0**，调用标识 **`$paper-evidence-framing`**。科研绘图可以配合 [FigureCraft](https://github.com/zlsjtj/FigureCraft) 使用，两者可独立安装。

## 安装

将仓库克隆到 Codex 的技能目录，目录名保留调用标识。以下命令适用于 PowerShell；设置了 `CODEX_HOME` 时使用该目录，否则使用用户目录下的 `.codex`。

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
git clone https://github.com/zlsjtj/PaperCraft.git (Join-Path $skillRoot 'paper-evidence-framing')
```

已有同名目录时先备份，不要覆盖正在使用的版本。在新会话中显式调用技能，可检查当前宿主是否识别了安装结果。自动发现由宿主管理；仓库中的配置允许隐式调用。

## 怎么用

直接提供论文和范围，例如：

> 使用 $paper-evidence-framing 修改这份论文。先指出影响理解的问题，再修订创新定位、工程解释和结果讨论。保留原始数据、公式和负结果，给我清稿、黄色审阅稿、PDF 和中文前后对照。

也可以只审阅、只改一段、继续上一版，或在实验未完成时整理已得到支持的内容。局部修改不会自动扩展成全文重写。

一次完整修订通常交付：

- 独立保存的清稿和黄色审阅稿；黄色表示本轮新增或改写的文字，删除、移动及图片替换另记。
- 中文诊断与代表性前后对照，说明原问题、改法、依据和仍未解决的部分。
- 图表的来源、修改状态、正文引用和实际入稿尺寸；新图应进入最终文件。
- 内容保护、页面检查和作者确认记录。文件检查通过不等于作者已经认可。

## 工具与依赖

阅读、判断和改写由宿主模型执行。脚本负责定位、受控写入和检查，不会自行证明创新性。

在自己选择的 Python 环境中安装依赖：

```powershell
python -m pip install -r requirements.txt
python scripts/check_dependencies.py . --require docx --require preservation --out runtime.json
python scripts/review_docx.py inspect manuscript.docx --out inventory.json
```

简单正文可按照 [清单格式](references/docx-helper.md) 编写补丁，再生成候选：

```powershell
python scripts/review_docx.py build manuscript.docx revision.json output --clean
python scripts/audit_preservation.py manuscript.docx output/manuscript_清洁候选稿.docx --out protection.json
```

输出目录应为新目录。含公式、域、交叉引用和混合格式的段落应走[复杂 Word 流程](references/complex-word.md)，不要强行交给简单段落工具。PDF 和逐页图片还需要宿主的 documents 技能、LibreOffice 与 Poppler；这些不随本仓库打包，详细说明见[依赖](references/dependencies.md)。

新版补充[选择规则复核与定范围审阅](references/method-transfer-audit.md)：检查训练配置如何映射到测试输入，并通过 `make_review_packet.py` 只提供明确选定的段落和图片。生成材料不等于完成独立审阅。

## 示例与检查

[检查点流水线示例](references/checkpoint-demo/input.md)提供原文、限定证据、英文改稿和中文改动记录。数据是教学构造值，不能作为研究结果引用。其他[完整示例](references/worked-examples.md)展示贡献、工程段和结果段的修改理由。

```powershell
python tests/run_tests.py --work-dir test-output/basic
python tests/run_preservation_tests.py --work-dir test-output/protection
python tests/run_integration_tests.py --out test-output/integration
python tests/run_effect_record_tests.py --out test-output/effect
python tests/run_review_packet_tests.py --out test-output/reading
python tests/run_representation_tests.py --out test-output/representations
```

原四组测试覆盖 66 项检查，新增定范围审阅材料测试 13 项、双表示入稿测试 8 项，共 87 项，使用临时教学文件。再次执行时换用新的输出目录。当前发布检查及未验证部分见 [验收记录](tests/acceptance-results.md)。

## 文件与发布范围

`SKILL.md` 是入口，`references/` 是具体方法，`templates/` 是工作记录，`scripts/` 和 `tests/` 是可执行工具及测试。

公开版保留当前功能代码，使用中文说明和匿名教学案例。私人稿件、未公开测量记录、本机路径、代理会话记录和历次生成缓存留在本地归档。英文论文示例、命令参数和第三方专有名称保留原文。来源见[来源说明](references/video-source-notes.md)，许可状态见 [LICENSE.md](LICENSE.md)。

包装不能补出不存在的研究贡献，也不能保证期刊初审。已经表达清楚的段落可以保留；缺实验、缺对照和缺来源应明确记录。
