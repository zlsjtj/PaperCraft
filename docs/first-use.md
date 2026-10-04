# 第一次用：只改标题和摘要

用一份公开的教学材料走完小任务，无需上传自己的论文。未安装技能时，先按[工具入口](install.md)安装；已经安装可直接开始。

## 下载材料，交给所用工具

1. [下载试用材料包](https://github.com/zlsjtj/PaperCraft/releases/download/v2.31.1/paper-evidence-framing-first-use.zip)并解压。包内是原始材料与任务，没有成品答案。
2. 本地工具读取整个目录；Claude 网页端上传 TASK.md 和 input/ 中的文件。
3. 复制下面这句话：

```text
使用 PaperCraft（paper-evidence-framing）。
按 TASK.md 处理 input/ 中的材料，
将结果另存到 output/，保留原文件。
```

## 拿到结果后

应得到Word 清稿、黄色审阅稿、PDF，以及简短中文改动说明。黄色表示本轮改写，不是 Word 原生修订。

先读标题和摘要：是否更快知道研究在比较什么，收益与代价是否说准确。再核对公式、表格、引用和已有标记。

完成后再看[公开案例](../examples/first-use-abstract/README.md)，比较它怎样组织解释，而非逐句或逐形照抄。首次试用与固定源码重建是两种检查，记录见[本轮范围](multihost-validation.md)。

如果只得到文字说明而没有文件，先确认工具具备文件读写和代码执行能力。缺少字体、Python 包或 PDF 渲染工具时，按[依赖说明](usage.md)处理；未完成的导出应单独说明。

<details>
<summary>用命令行准备同一份材料</summary>

在已安装技能的根目录运行：

```text
python scripts/first_run.py --host codex --out ../PaperCraft-try
```

`--host` 可换成 `claude-code`、`claude` 或 `workbuddy`。不传时仍为 Codex，兼容旧命令。输出目录必须是新目录，且位于技能目录外。

这条命令只复制材料、准备 TASK.md，不调用模型、不生成成品、不安装依赖。`claude` 使用相对附件路径；本地宿主的任务会指明实际技能路径。environment.json 是环境查找记录，不是运行结果。命令会显示所用 Python 和缺少的模块；材料准备成功不代表该 Python 已能导出成品。云端任务不检查本机 Python。

</details>

## 换成自己的材料

提供原稿、实现说明和结果表，先明确要改的章节。说明沿用了什么、改了什么，但不必提前替技能总结创新点。

材料不足时先完成有依据的部分，缺项单独列出。保留原件，新结果另存。

## 换一个客户端准备任务

从任意目录运行技能内脚本的实际路径。WorkBuddy 附件模式不携带维护者路径：

```text
python /path/to/SKILL_ROOT/scripts/first_run.py --host workbuddy --portable --out ../workbuddy-try
python /path/to/SKILL_ROOT/scripts/first_run.py --host claude-code --installation plugin --out ../claude-try
```

插件任务自动使用带命名空间的调用标识；不传 `--installation` 仍是个人技能入口。不传 `--host` 仍是 Codex。输出目录应在技能目录外且未存在。以上命令只准备材料，随后把 TASK.md 交给所选客户端执行。
