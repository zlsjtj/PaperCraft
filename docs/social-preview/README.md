# PaperCraft 分享预览

[PNG](social-preview.png) · [可编辑 SVG](social-preview.svg) · [PDF](social-preview.pdf) · [布局内容](layout.json)

用于分享仓库链接时的预览，1280 × 640。正文取自[压头锁止案例](../../examples/clamp-timing/README.md)的中文摘述，展示“列步骤与数字”到“先解释何时锁止及收益、代价”的变化。数值为教学构造值；不是新实验、实时生成截图或录用证明。完整条件与英文稿仍看原案例。

采用已有作品排版，没有重新生成科研图或使用新的图像模型。字体、配色和导航层级与 FigureCraft 配套。SVG 保留文字、线和颜色；打开 SVG 时需要对应字体，PDF 已嵌入所用字形。没有分发字体文件。

## 重建

需要 Python 的 `reportlab`、`pypdf`，支持中文的 TrueType 字体（可为 TTC），以及 Poppler 的 `pdftoppm`。在仓库根目录执行，将占位替换为本机路径：

```text
python docs/social-preview/build.py --out ../PaperCraft-share --font CJK_TTF --bold-font CJK_BOLD_TTF --latin-font LATIN_TTF --latin-bold-font LATIN_BOLD_TTF --pdftoppm PDFTOPPM
```

输出目录必须不存在且在仓库外。工具检查文字越界、PDF 文字、PNG 尺寸和体积；`build-record.json` 保存来源、字体及输出哈希。这些检查不能证明版式好看，需要打开实际 PNG 复核。

生成 PNG 后，在仓库 Settings → Social preview 上传；本地重建不会上传或改设置。[GitHub 说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)

该图未重复插入首页；首页已有可直接阅读的前后文，分享图也不代替清稿与审阅稿的下载入口。
