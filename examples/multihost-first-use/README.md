# 从安装包完成一次标题与摘要修改

[清稿 Word](clean.docx) · [清稿 PDF](clean.pdf) · [审阅稿 Word](review.docx) · [审阅稿 PDF](review.pdf) · [改动说明](report.pdf)

输入为[公开压头案例](../clamp-timing/input/)，本次仅修改标题与摘要。第一次生成的摘要较长，把参考资料挤到第三页；重读后压缩为两页，正文对象不变。最终页数来自真实渲染，未调小字号。

在仓库根目录重建最终文字：

```text
python scripts/review_docx.py build examples/clamp-timing/input/rough.docx examples/multihost-first-use/plan.json ../paper-trial-output --clean
python scripts/render_review.py ../paper-trial-output/rough_清洁候选稿.docx ../paper-trial-pages --soffice SOFFICE --pdftoppm PDFTOPPM
```

这两条命令重建既定改稿；重新调用技能生成，用[原始试用材料](../../docs/first-use.md)。公式、表格、域、超链接及标题摘要以外的正文 XML 已核对。原有黄色标记保留，审阅稿新增两处黄标。输入没有嵌入图，本任务没有补画占位图。

这是当前维护上下文对已知教学材料的执行验证，不是独立新材料测试，也没有证明其他宿主已经能够完成任务。
