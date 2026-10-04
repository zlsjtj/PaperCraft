# 第一次用：先改一份教学稿的摘要

先用公开材料走通一次，再处理自己的论文。这次只改标题和摘要，其他段落与文档对象保留。无需准备真实稿件，也不需要 FigureCraft。

## 1. 准备材料

按[首页](../README.md#开始使用)安装后，在 PowerShell 运行：

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
python (Join-Path $skillRoot 'paper-evidence-framing/scripts/first_run.py') --out './PaperCraft-try'
```

`python` 要指向可用的 Python 3；若本机命令是 `python3`，相应替换。输出目录必须不存在，并放在技能文件夹外。

命令复制原稿 Word、便于阅读的文本、实现说明和结果表，生成 `TASK.md`。**它只准备任务，不调用模型、不改稿，也不安装依赖。** 原始任务要求改全文，这里的任务已收窄为标题与摘要；成品和评阅没有混入输入。

## 2. 交给 Codex

在一个新的 Codex 会话中，把下面的路径换成上一步打印的绝对路径：

```text
请执行 C:/你的试用目录/PaperCraft-try/TASK.md 中的首次试用任务。
```

Codex 会读取指定的 `SKILL.md` 和 `input/`，将结果写入独立 `output/`。先确认它找到了技能和原稿，再开始编辑。材料里的数字全部是教学构造值，输出仍应保留这一标记。

准备命令只需 Python 标准库；Word 编辑需要 `lxml`、`python-docx` 等包，PDF 渲染还需要文档工具、LibreOffice 和 Poppler。`environment.json` 只记录查找到的模块和程序，**不是运行通过的证明**。缺依赖时按[进阶使用](usage.md)处理，或让 Codex 明确报告缺少的项目；没有 PDF 时不能说页面检查已完成。

## 3. 看结果是否值得留下

先打开清稿和审阅稿，问三个问题：原来在比什么，现在是否更快看出来？数据说明了收益，也交代了代价吗？摘要之外的公式、表格、引用和已有高亮是否保留？

预期得到独立 Word 清稿、黄色审阅稿、对应 PDF 和简短中文说明。黄色表示本轮文字变化，不是 Word 原生修订。不要用文件数量或字数变化替代阅读判断。

本轮按这个范围得到的[局部清稿与审阅稿](../examples/first-use-abstract/README.md)可供对照。

完成后再看[公开完整案例](../examples/clamp-timing/README.md)。它修过全文和图件，所以文件不会与你这次局部任务相同，也不是必须照抄的标准答案。你可以比较开头如何交代问题、对照和限制。

## 换成自己的材料

提供稿件、实现说明和结果表，明确本次修改范围。实现说明不必先替技能总结创新点，但要讲清哪些部件、算法和设置是沿用的，哪些做法是新增的。数据不全时先修改有依据的内容，研究缺口另列。

准备器的保护性检查：`python tests/test_first_run.py`（在仓库根目录）。它也已纳入现有单元测试发现入口。首次试用验证范围见[记录](first-use-validation.md)。
