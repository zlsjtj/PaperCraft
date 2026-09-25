# 从独立图到最终图文稿

适用于全文图文联合修订。只审阅、单图导出或单段修改不强制这条路径。

## 成稿才是最终检查对象

维护全部图的简表：图号与正文位置、保留/修改及原因、源文件、实际嵌入文件、尺寸、图注和正文引用、待解决项。正确清楚的图可以保留；保留也是明确决定，不等于遗漏。

拿到图形候选后，把选定版本嵌入独立论文候选，更新必要图注和正文，再渲染最终 Word。无需先征求“是否允许嵌图”，如果用户已授权联合修订，入稿属于该工作；不覆盖原件。作者最后确认确切版本。

只有独立图时写“单图候选完成、入稿未完成”。不能用图文件已生成或黄色文字已修改，代替联合稿已完成。图像不显示黄标时，在中文对照首页直接放原/新图和所在页，不在学术正文插工作标记。

最终逐图核对：新图是否真正进入 Word；是否替错图；图注和正文仍对应；有无缩放失真、裁剪、小字、分页问题；其他图是否被意外改变。最终图片字节与尺寸匹配后，仍需看图和每页渲染。

## 可选的只读绑定检查

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
