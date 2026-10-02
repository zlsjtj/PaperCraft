# 三腔压力夹具：一次完整图文迁移示例

这是**原创合成 DEMO**。装置、工况、时间、压力差和泄漏结果都是固定编辑材料；没有实物试验、真实客户、已发表结果或首创证明。该例是一轮候选技能在新上下文中的完整迁移，**不是普通模型与旧技能的受控比较，也不是通用 Nature 质量证明**。

## 直接查看成稿

- [最终英文清稿](final-delivery/clean.docx)与[黄色审阅稿](final-delivery/review.docx)
- [清稿PDF](final-delivery/clean.pdf)、[审阅稿PDF](final-delivery/review.pdf)
- [中文图文前后对照简报](editorial-report-final.docx)与[PDF](editorial-report-final.pdf)
- [最终机制图](final-figure/figure.png)、[SVG](final-figure/figure.svg)、[PDF](final-figure/figure.pdf)、[可编辑场景](final-authored/figure_spec.json)
- [图注](final-authored/caption.txt)与[替代文字](final-authored/alt_text.txt)
- [完整文字补丁](final-authored/authored-edits.json)和[简短验收](ACCEPTANCE.md)

![最终机制图](final-figure/figure.png)

## 实际选择与修复顺序

原文介绍部件，原图只列四类组件。改稿先承认软管式基线已经具有共同参考压力，再解释实际改变：三个样品模块的位置保持不动，用一个可更换参考底座替代三根参考软管。时间收益与泄漏资格、压力差的变化共同解释；完整九条记录和两次失败后的 NA 均保留。

主图选用装配状态的剖面。三个闭合隔膜上方是各自隔离的样品，下方是同一个连续参考空间；无箭头穿膜。它让隔离与共享同时可见。未选的展开候选便于想到拆换，但削弱了隔膜与参考空间的直接邻接，且定位销引线在平移后悬空。两者的实际图均保留，不把失败候选隐藏。

1. `first-complete-v1/` 与 `first-figure/` 保留第一份完整稿。`first-authored-complete/entry-candidates.md` 保留两种实际入口文字。
2. `final-complete/` 是一次模型自修后的文稿。自修将穿过参考腔标签的密封垫引线移至外侧，并在摘要直接说明两种条件的压力差增加 0.01 kPa。记录见 `final-authored/self-review.json`。
3. `final-delivery/` 在自修稿之后仅追加主编辑者指出的表头版式修复：代码式长表头改为易读标签，调整列宽、粗体和浅底色。九条数据行的完整规范化 XML 保持一致，**整表 XML 不再相同**；没有修改科学正文或图。该步不会倒写为第一次生成已经做到。

黄色表示本轮新写普通文字，不是 Word 原生修订。表头版式变化由单独记录说明。图采用 160×85 mm、平面剖面与最小 9.45 pt 标签；剖面中一片密封垫呈多个断面，图注负责解释这一约定。基线软管关系由正文承担。

## 从新目录重建

需要 Python 3、python-docx、lxml、reportlab、pypdf、Pillow、numpy、Arial 字体和 Poppler 的 `pdftoppm`。使用宿主已有依赖，本例不会安装或下载软件。PaperCraft 必须包含正式的文字、替图、报告工具；FigureCraft 必须包含场景渲染器。

把本目录的六个 `.py` 脚本及 `input/` 复制到任意新目录。随后从另一个工作目录运行，显式传入依赖路径；输出目录必须不存在：

```text
python PATH_TO_COPIED_EXAMPLE/rebuild.py --input PATH_TO_COPIED_EXAMPLE/input --paper-skill PATH_TO_PAPERCRAFT --figure-skill PATH_TO_FIGURECRAFT --font PATH_TO_ARIAL_TTF --pdftoppm PATH_TO_PDFTOPPM --out NEW_OUTPUT_DIRECTORY
```

六个脚本为 `author_trial.py`、`self_review_and_repair.py`、`integrate.py`、`finish_table.py`、`finish_records.py`、`rebuild.py`。它们依次调用真实的 `apply_authored_edits.py`、`apply_figure_edits.py`、`audit_figure_integration.py`、`build_editorial_report.py` 与 FigureCraft 渲染器。`finish_table.py` 只适用于本例的已知表头与九条数据，不是通用 Word 编辑器。

输出包括首稿、自修稿、最终交付稿、图源/导出、实际图文简报和工具收据。`rebuild-commands.json` 与载入文件收据含执行机器路径，只用于私下复核，不应复制进公开示例。固定重建不算第二次自然语言生成试用。

最终 Word/PDF 页面由宿主 documents 工作流另外渲染；脚本保存成功不等于页面验收，模型审阅不等于作者或人类专家认可。
