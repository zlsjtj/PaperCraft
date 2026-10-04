# 兼容范围

调用标识仍为 `paper-evidence-framing`，原有 Python 命令保持兼容。实际使用哪一版，应以宿主读取的 `SKILL.md` 路径和内容为准；更新仓库或下载 ZIP 不会自动更新已安装副本。包内 `package-manifest.json` 记录来源与文件哈希。当前版本与已验证宿主范围见[安装记录](docs/multihost-validation.md)，早期版本结果保留在[历史验收](tests/acceptance-results.md)。

## Word 修改能力

先运行 `review_docx.py inspect`，按能力清单选择工具，不只看兼容字段 `editable`。

- 整段替换、插入、删除、移动及有限格式修改：仅在 `whole_paragraph.available` 允许时执行。含复杂对象、混合格式或已有高亮的目标仍受保护；历史原生修订也会阻断整段操作。
- 普通文字片段：复杂段落中满足条件的连续同格式文字可用 `replace_span` 修改。公式、域、超链接、已有高亮与历史修订原样保留，不能跨越这些边界匹配。
- 已写好的较长改稿：按 `authored_prose_diff` 能力及[复杂 Word 说明](references/complex-word.md)接续；可用路线不等于任意新文字都已获准修改。

工具不接受、拒绝或抹除历史修订。黄色高亮表示本轮改写，不是 Word 原生 Track Changes。表内文字、公式重写、刷新交叉引用域等不在上述片段编辑器的能力内，需要另选合适工具并检查确切产物。清单字段、调用示例及拒绝条件见[工具说明](references/docx-helper.md)。

## 导出与验证

Word 导出可使用独立 LibreOffice 与 Poppler 路径，也保留已有 documents 适配器；依赖和命令见[使用说明](docs/usage.md)。ZIP、XML、哈希和字段检查不能代替页面检查，更不能证明论文更有说服力。字体、宿主或文档引擎变化后，应重新打开并核对最终文件。
