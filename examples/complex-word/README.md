# 复杂段落的局部续改

本例只修正热模型示意中的一句过强表述。原生公式、斜体变量、REF域和缓存结果、超链接、历史插入删除、绿色高亮、两列表格及嵌入图均保留。数据为教学构造；小图只是包保护哨兵，不是科研配图。

从仓库根目录运行，使用新的输出目录：

```powershell
python examples/complex-word/build_fixture.py --out demo-source
python scripts/review_docx.py build demo-source/input.docx demo-source/plan.json demo-output --clean
python scripts/review_docx.py verify demo-source/input.docx demo-output/input_清洁候选稿.docx
python scripts/audit_preservation.py demo-source/input.docx demo-output/input_清洁候选稿.docx --out preservation.json
```

生成清稿、黄色审阅稿、简短中文修改记录和映射。清稿保留历史原生修订，不代表接受它们。修改仅针对普通文字片段；公式或域结果不是可替换的文本。黄色只标本轮改写，删除靠记录呈现。

若需要改公式本身、超链接目标或历史修订内文字，当前接口会定位拒绝，不会输出半份修改。不要通过整段清空绕过保护。该例的像素小图仅覆盖包保留；真实图形内容和版面必须另看最终渲染。

PDF需现有documents渲染器、LibreOffice和Poppler，未随仓库分发。模型辅助页面查看、真人认可与上述结构检查分别记录。
