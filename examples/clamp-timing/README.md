# 何时锁住压头：把操作记录写成研究问题

**[看后续完整图文版：三页论文、两张图与全部数据](complete/README.md)。** 本页保留此前改写、首评与修复记录；后续版本继续使用同一套公开材料。

可转动的压头便于贴合斜面，加载时继续保持自由却可能产生漂移。这个案例比较不同锁止时机，展示如何把模式与结果清单写成有重点的论文。**材料和九行数值均为教学构造，不是真实实验。**

[读清稿 PDF](clean.pdf) · [看黄色修改](review.pdf) · [下载 Word 清稿](clean.docx) · [下载 Word 审阅稿](review.docx)

[![创新定位、技术工作与完整成稿的前后对照](showcase/assets/contribution.png)](showcase/README.md)

**[看完整三步对照](showcase/README.md)** · [30 秒导览](showcase/assets/tour.gif)

## 改写抓住了什么

- 把“何时锁住已有压头”放在前面，不把已有转动结构写成新部件。
- 在同一斜面条件下讲清取舍：先就位再锁定，相比全程自由，漂移从 125 μm 降至 19 μm，就位时间从 17 秒增至 32 秒。
- 预载保持、锁定时不抬起压头等工作，在方法中解释其必要性。平面没有重复性收益、另一方向的斜面未得到矫正，也保留在稿中。

黄色表示相对原稿的本轮改写，不是 Word 原生修订。原有黄色声明仍保留。不同版本各有优缺点，完整比较放在下方。

## 用什么材料

[原稿文字](input/rough.txt) · [原稿 Word](input/rough.docx) · [实现说明](input/implementation.md) · [九行结果](input/results.csv)

想自己试改，先按[首次任务](../../docs/first-use.md)使用公开材料；想原样重建本页文件，使用下面的脚本。

## 重建这份演示

需要本仓库、FigureCraft完整包、Python及两个仓库的requirements、Arial和Poppler。在本例目录执行，输出目录必须不存在：

```powershell
python -B build_after_review.py --input input --out rebuilt --stage after-review --papercraft ../.. --figurecraft FIGURECRAFT_ROOT --font ARIAL_TTF --pdftoppm PDFTOPPM
python -B verify_trial.py rebuilt --papercraft ../..
```

参数路径替换为实际位置。脚本生成可编辑SVG/PDF/PNG、清稿与审阅稿；Word转PDF使用宿主文档渲染器。不要把固定源码重建当成从新材料再次创作。

<details>
<summary>比较怎么做的，以及仍未验证的部分</summary>

这是原创构造演示，没有真实实验。输入包含未预写贡献的原稿、实现说明和九行结果；两次独立执行分别使用旧版与新版技能。相同模型、材料和范围，但执行预算未严格等额，每臂一次生成加一次自修。本轮没有普通提示臂或真人测试。

旧稿和新稿都识别出锁止时机的取舍。新版更直接给出准备时间与漂移的代价；旧版指标定义、结果组织和转动表达有优势。匿名模型首评未判新版全面胜出。根据具体反馈，新稿补明确末端力CV、接近前锁定的时机、已有销轴的转动弧线和下压板标签归属。首图与评后图分开保留。

`clean.docx`、`review.docx`及PDF是最终演示；黄色修改相对input/rough.docx，保留原有黄色声明，不是Word原生修订。`comparison/model-review.md`保留首评与非盲定向复验；报告中的本地审阅路径只表示历史位置，不是外部依赖。旧版对照PDF修复了Word的SVG字距问题，其最终嵌图约200 dpi，外部SVG仍保留。当前新稿使用正常SVG表示。

公式XML、九行表值、斜体、REF、书签、超链接和已有黄色已逐内容核对。最终三页Word/PDF另经模型逐页查看。缺真实读者、物理实验和跨题材统计性验证；本例经反馈开发后不再算未见任务。

</details>
