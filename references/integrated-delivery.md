# 从独立图到最终图文稿

适用于全文图文联合修订。只审阅、单图导出或单段修改不强制这条路径。

## 成稿才是最终检查对象

先核真实输入再决定整套能改到哪里。用现有图绑定工具取全部drawing与尺寸；有FigureCraft时可用其 `inspect_figure_sources.py` 对照外部源，区分字节相同、像素相同但编码不同、需要人工确认的不同资源。没有这个工具时直接核相同事实，不强制安装另一个技能。源文件名、较大尺寸和DPI标签都不能单独证明图的身份或更高科学质量。

实际分流：有原始数据/可编辑图源时可重绘；有经核实的更完整原图时恢复原图字节；只有测量栅格时保留曲线、照片、标尺和原像素，只改有依据的图组位置、尺寸及图文职责。论文表内已有汇总可以另画明确口径的比较，不能冒充重建原曲线。机制示意依已有事实独立设计，不受实验曲线缺源牵连。缺源影响的是具体操作，不让整篇停止，也不把源受限保留记成视觉提升。

随后维护全部图的短表：图号/正文位置、它支撑的判断、实际源、嵌入资源、尺寸、保留或调整及理由、图注和剩余项。按[图组与论证的接续](presentation-review.md)选定整组，避免只改最容易重画的一幅主图就称整套完成。已经清楚的图可以保留；已审阅、已改善、源受限是不同结论。

拿到图形候选后，把选定版本嵌入独立论文候选，更新必要图注和正文，再渲染最终 Word。无需先征求“是否允许嵌图”，如果用户已授权联合修订，入稿属于该工作；不覆盖原件。作者最后确认确切版本。

只有独立图时写“单图候选完成、入稿未完成”。不能用图文件已生成或黄色文字已修改，代替联合稿已完成。图像不显示黄标时，在中文对照首页直接放原/新图和所在页，不在学术正文插工作标记。

最终逐图核对：新图是否真正进入 Word；是否替错图；图注和正文仍对应；有无缩放失真、裁剪、小字、分页问题；其他图是否被意外改变。最终图片字节与尺寸匹配后，仍需看图和每页渲染。

对于视觉提升任务，还要看同页上的实际表现：主图是否被长图注或重复正文淹没，主对象、局部与标签是否有清楚层次，空间表达是否帮助理解而未诱发错误。先核科学关系，再判断表达与美观；不能因一个层次通过而替另一个层次签字。独立图更漂亮但入稿后更难读属于退步，应修复或保留旧版。完整操作案例见[过滤组件](../examples/visual-editorial/README.md)。

## 实际写入与接续

先完成有来源的文字补丁，图注也属于这份补丁。`apply_authored_edits.py` 将相同补丁分别写成清稿和本轮黄标稿；它保护原生公式、字段和已有修订，支持在普通文字边界受控分段。支持范围见[复杂 Word 路径](complex-word.md)。

```text
python scripts/apply_authored_edits.py --source parent.docx --edits authored-edits.json --skill . --out text-stage
python scripts/apply_figure_edits.py text-stage/clean.docx clean-images.json final-clean.docx --receipt clean-images-receipt.json
python scripts/apply_figure_edits.py text-stage/review.docx review-images.json final-review.docx --receipt review-images-receipt.json
```

替图清单以**对应文字输出**的 SHA256 为基线；清稿和黄标稿哈希不同，分别建清单。每项指定 `drawing_index`，以及其全部 `representations`：`kind`、原 `part`、`old_media_sha256`、选中 `source_asset`、`source_asset_sha256`。相对资源路径从清单所在目录解析。先用 `audit_figure_integration.inspect()` 取得实际媒体映射，不从文件名猜图号。完整字段见脚本帮助和原创完整交付示例。

此工具只替换同编码、相同比例的主文档 PNG、JPEG 与 SVG 媒体，保留正文 XML、关系和其他 ZIP 成员。JPEG 的 .jpg/.jpeg 可互用，必须实解码验证，按原字节写入；非正常 EXIF 方向拒绝并另行审阅，不静默重编码或转正。漏交 SVG、基线过期、跨图共用媒体、无法可靠定位的结构均拒绝写出，防止一种查看器显示新版而另一种仍显示旧图。改变图框比例、增加图号或复杂 fallback 仍走格式感知编辑，不声称工具覆盖全部 Word。报告技术写入结果不代表科学或审美通过。

中文简报先放真实文字和图片前后对照，再记录改善与代价。最后主编辑者打开**已合图**的整篇输出，检查入口、方法、证据和结论接续；分工者的单项通过不能替代这一步。对已知可修缺口先修作品，不另开无关示例转移验收。保护检查、逐页阅读和作者认可仍分别记录。

需要简短 Word 对照时可用 `python scripts/build_editorial_report.py report.json report.docx`。JSON 提供人工撰写的 `title`、`summary`、`baseline`、`changes`、`checks`、`remaining`；`figures` 中传入真实前后图片，脚本不自动生成效果结论。字段与完整材料见 `examples/complete-fixture`。既有 `review_docx.py build` 的完整/局部报告接口仍可使用；没有必要为同一任务两套都生成。

## 只读绑定检查

`scripts/audit_figure_integration.py` 只核对主文档 DrawingML 图像。适合有明确图像映射的 Word 联合稿；复杂 fallback、VML 或外部图片应由格式感知流程继续处理，不能因工具不支持而静默漏掉。

```text
python scripts/audit_figure_integration.py final.docx figures.json --parent parent.docx --out integration.json
```

`figures.json` 是最终输出清单，不从期待的状态直接制造通过：先提取实际源/图号，保留预期导出哈希，再验证真实 Word。

```json
{
  "scope": "all-main-document-drawings",
  "figures": [{
    "id": "Figure 4",
    "drawing_index": 4,
    "disposition": "revised",
    "media_sha256": "hash of selected PNG",
    "placement_width_mm": 157.48,
    "placement_height_mm": 100,
    "caption_contains": "Figure 4.",
    "source_asset": "../figure/selected/figure.png",
    "source_asset_sha256": "hash of selected PNG"
  }]
}
```

示例仅展示一条，真实清单须含全部主文档 drawing，顺序从1开始。`preserved` 要求与父稿媒体字节相同；`revised` 要求不同且绑定实际导出。未改图如只调整尺寸仍用 `preserved`，在人工清单写明版式修改。无图注的装饰对象可显式给 `kind: decorative` 和 `reason`，不能假作科研图绕过检查。

可选 `docx_sha256`、`parent_sha256` 防止拿错版本；宽度容差0.05 mm。检查器不验证图注语义、正文引用或实际字号；不是渲染器，也不保证外来 Word 全面覆盖。技术失败时 `overall_status` 为 `FAIL`，其余情况保留 `REVIEW_REQUIRED`；技术通过必须与科学、视觉、作者认可分开报告。

如果本轮改了图注，再给 `caption_exact` 绑定最终完整可见文字；可以检出跨run编辑时丢空格等差异。复杂公式/字段图注不能仅靠 `w:t` 拼接验收，按限制人工核对。`caption_contains` 只用于确认可见定位文本存在，不能替代全文一致性。

## SVG 和 PNG 双表示

DrawingML 的 `a:blip` 可能只是 PNG 回退图，`asvg:svgBlip` 另指一个 SVG。不同渲染器会选用不同表示；只替换其中一种会导致论文仍显示旧图。新版入稿清单可逐图添加 `representations` 数组，每项含 `kind`（`primary` 或 `svg`）、`media_sha256`、`source_asset` 和 `source_asset_sha256`。主图原字段仍保留，表示集合必须完整。文件相同只证明绑定，仍要查看最终页面。

`audit_figure_integration.py` 会核对两种嵌入内容与各自导出。多表示图片沿用旧清单时进入待审，不能拿只核对 PNG 的结果当整张图通过。每次替换后重新渲染；记录失败首轮和修复后的确切文件。
