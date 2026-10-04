# 第一次用：只改标题和摘要

先用公开的教学材料完成一个小任务。材料是构造示例，不需要上传未发表论文。先按[工具入口](install.md)安装技能。

## 直接拿材料试

1. [下载试用材料包](downloads/paper-evidence-framing-first-use.zip)并解压。
2. 本地工具读取整个目录；Claude 网页端上传 TASK.md 和 input/ 中的文件。
3. 告诉所用工具：**使用 PaperCraft（paper-evidence-framing），执行 TASK.md，把结果放进独立 output/。**

包中只有原始材料和任务要求，没有改写答案或已选构图。不需要先运行准备脚本。导出文件需要宿主环境中的实际依赖；安装步骤与[依赖说明](usage.md)分开。

## 喜欢用命令行时

在已安装技能的根目录运行：

```text
python scripts/first_run.py --host codex --out ../PaperCraft-try
```

`--host` 可换成 `claude-code`、`claude` 或 `workbuddy`。不传时仍为 Codex，兼容旧命令。输出目录必须是新目录，且位于技能目录外。

这条命令只复制材料、准备 TASK.md，不调用模型、不生成成品、不安装依赖。`claude` 使用相对附件路径；本地宿主的任务会指明实际技能路径。environment.json 是环境查找记录，不是运行结果。命令会显示所用 Python 和缺少的模块；材料准备成功不代表该 Python 已能导出成品。云端任务不检查本机 Python。

## 拿到什么，怎么看

得到独立 Word 清稿、黄色审阅稿、PDF 和简短中文说明。黄色表示本轮改写，不是原生 Track Changes。先看读者是否更快知道研究在比较什么、收益与代价是否说准确，再核对摘要之外的公式、表格、引用和已有标记。

字体、模块或 PDF 渲染缺失时，应说明未完成的导出，不把文件存在当作视觉验收。作品效果仍需阅读和看图。

完成后再看[公开案例](../examples/first-use-abstract/README.md)，比较它怎样组织解释，而非逐句或逐形照抄。首次试用与固定源码重建是两种检查，记录见[本轮范围](multihost-validation.md)。

## 换成自己的材料

提供原稿、实现说明和结果表，先明确要改的章节。说明沿用了什么、改了什么，但不必提前替技能总结创新点。

材料不足时先完成有依据的部分，缺项单独列出。保留原件，新结果另存。
