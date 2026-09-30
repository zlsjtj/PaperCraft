# 有界缓存：先承认简单办法已经解决什么

这是原创写作 DEMO，所有结果由手工构造，没有实现、仿真或实验。三篇真实论文只作机制来源，不是本例已运行的对照。材料没有预写贡献答案；原稿、实现说明、完整20行数值及来源在 material-paper/。

修改前技能与候选技能分别在新上下文中写作；各有一次自主修订。paper-old/ 与 paper-new/ 保留首稿和自修稿。独立模型先读匿名等长前部，再读全文；它更偏好新版用“1 MiB需要256个4 KiB对象的空间”建立困难，并把相同扫描上限下的提前腾空代价放到主线上。旧版对64与48的预算差异限定更明确，不能丢掉这项优点。paper-new/delivery.md 是吸收反馈后的交付，不冒充首次生成。

最终文稿保留完整数值、负例、真实文献来源和研究缺口。它没有证明该缓存设计的新颖性或性能；本例检验的是从材料提炼有意义且有限的判断。没有普通提示组、严格token配额、重复生成或真人阅读，不能概括为普遍胜出。

## 查看

- [清稿](document/clean.docx)、[PDF](document/clean.pdf)、[黄色审阅稿](document/review.docx)、[审阅PDF](document/review.pdf)。黄色相对旧技能稿，按段落标新写内容，不是Word原生修订。
- [旧技能PDF](document/before.pdf)。两稿使用同一示意图与排版，避免把字体与图形差异当文字能力。
- 共用图是维护者依据已知事实制作的入稿辅助，不计作独立绘图效果验证。

## 重建

在仓库根目录，准备python-docx、reportlab、Pillow、pypdf及字体；PNG需要Poppler。将下列路径换成实际路径：

```powershell
python examples/cache-reserve/build_cache_figure.py --out new-cache-figure --font C:/Windows/Fonts/arial.ttf --bold-font C:/Windows/Fonts/arialbd.ttf --pdftoppm /path/to/pdftoppm
python examples/cache-reserve/build_manuscripts.py --root examples/cache-reserve --paper-skill . --out new-cache-documents --font C:/Windows/Fonts/times.ttf --bold-font C:/Windows/Fonts/timesbd.ttf
```

第二条默认绑定 examples/cache-reserve/cache-figure/figure.png。如需验证刚重建的图，先在新的示例副本内把它替换为对应输出，再运行；不要覆盖已保留的首次产物。Word转PDF使用宿主documents技能或LibreOffice，转换后必须实际查看页面。源码重建只证明文件流程可执行，不代表模型在新材料上会作出相同选择。
