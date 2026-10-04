# 锁止时序 从记录清单到条件性选择

这是原创构造演示，没有真实实验。输入包含未预写贡献的原稿、实现说明和九行结果；两次独立执行分别使用旧版与新版技能。相同模型、材料和范围，但执行预算未严格等额，每臂一次生成加一次自修。本轮没有普通提示臂或真人测试。

旧稿和新稿都识别出锁止时机的取舍。新版更直接给出准备时间与漂移的代价；旧版指标定义、结果组织和转动表达有优势。匿名模型首评未判新版全面胜出。根据具体反馈，新稿补明确末端力CV、接近前锁定的时机、已有销轴的转动弧线和下压板标签归属。首图与评后图分开保留。

`clean.docx`、`review.docx`及PDF是最终演示；黄色修改相对input/rough.docx，保留原有黄色声明，不是Word原生修订。`comparison/model-review.md`保留首评与非盲定向复验；报告中的本地审阅路径只表示历史位置，不是外部依赖。旧版对照PDF修复了Word的SVG字距问题，其最终嵌图约200 dpi，外部SVG仍保留。当前新稿使用正常SVG表示。

## 重建

需要本仓库、FigureCraft完整包、Python及两个仓库的requirements、Arial和Poppler。在本例目录执行，输出目录必须不存在：

```powershell
python -B build_after_review.py --input input --out rebuilt --stage after-review --papercraft ../.. --figurecraft FIGURECRAFT_ROOT --font ARIAL_TTF --pdftoppm PDFTOPPM
python -B verify_trial.py rebuilt --papercraft ../..
```

参数路径替换为实际位置。脚本生成可编辑SVG/PDF/PNG、清稿与审阅稿；Word转PDF使用宿主文档渲染器。不要把固定源码重建当成从新材料再次创作。

公式XML、九行表值、斜体、REF、书签、超链接和已有黄色已逐内容核对。最终三页Word/PDF另经模型逐页查看。缺真实读者、物理实验和跨题材统计性验证；本例经反馈开发后不再算未见任务。
