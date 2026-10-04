# 首次试用：只改标题与摘要

这份局部修订使用公开的[压头教学材料](../clamp-timing/input/)。数字都是构造值。维护者已看过完整案例，所以本次只验证首次试用路径，不作为新材料能力或独立盲测。

[原稿 PDF](before.pdf) · [清稿 Word](clean.docx) · [清稿 PDF](clean.pdf) · [黄色审阅稿 Word](review.docx) · [黄色审阅稿 PDF](review.pdf)

标题与摘要前置锁止时序、漂移与准备时间的取舍；方法、表格、公式、引用、超链接和旧高亮保持原样。图片占位符也是原稿内容，本次没有新增图。要看包含图件的全文修订，见[完整案例](../clamp-timing/README.md)。

局部试用初稿把标题和摘要写得太长，来源说明被挤到第三页；收短后清稿、黄稿均为两页。首次措辞中可能混淆比较顺序的 respectively 已去掉，最终数字直接绑定比较对象。没有缩小字体或删除正文来省页数。

在仓库根目录，用新输出目录重建这份固定改稿：

```powershell
python scripts/review_docx.py build examples/clamp-timing/input/rough.docx examples/first-use-abstract/plan.json rebuilt-abstract --clean
```

`plan.json` 保存实际改写和依据；这条命令复现既定修订，不调用模型。想让技能自己判断，使用[首次试用入口](../../docs/first-use.md)。PDF 需另行渲染，不能仅改扩展名。

逐段 XML 对照确认只有 P0002 标题和 P0004 摘要变化，其余段落、表格及其他 ZIP 部件保持一致。清稿和审阅稿的四页实际渲染均已由维护模型查看：公式、表格、来源与高亮可读，没有裁切或空白尾页。此处清稿保留了输入已有的黄色高亮；审阅稿另增加本轮两段黄色。核对哈希见[记录](validation.json)。没有真人认可或本轮原生 Word 打开测试。
