# 让选择规则可以复现

“先校准、再冻结、最后测试”只交代了顺序。若训练与测试的规模、对象或配置不同，审阅者还要能回答：一个具体测试输入如何找到那条已经冻结的规则？

抽取一个稿内已有的测试例，核对输入特征、分桶/归一化、查表键、未命中时的回退。不能从“测试成功”反推规则正确，也不能把实现支持范围写成实测覆盖范围。若正文说不清，先查与当前结果绑定的源码、冻结表及来源哈希；当前工作树的同名函数未必属于稿件版本。

只补缺失的定义或定位，不把实现细节全部搬进正文。特别检查两个含义相近的术语是否实际不同，例如选择前的形状特征与选定内核后的执行参数。已经充分的贡献、结果和限制段可以保留。

## 教学例

原句：`The policy is calibrated on small and large inputs and then frozen before testing.`

如果相应版本的配置确实规定两个桶，可改为：`The lookup uses input size and layout class. Inputs up to the recorded boundary use the small-input bucket; larger tested inputs use the large-input bucket. A missing key retains the reference path.`

这段只有在边界数值、布局分类、默认路径可查证时才能成立。正式稿应写出实际边界或精确引用表格；这里的匿名教学句不是可以直接套用的成品。若来源未绑定，诊断应写“缺少映射定义”，不能猜一个合理阈值。

## 精确提供首次阅读材料

先用 `review_docx.py inspect` 得到正文段落 ID 和文本哈希。编辑者为两版选择同等范围的标题、摘要、贡献段、核心图及图注，写 selection JSON，再运行：

```text
python scripts/make_review_packet.py manuscript.docx selection.json --out first-reading
```

JSON 包含 `source_sha256`、`purpose` 和 `paragraphs`；每个段落只含 `id`、`text_sha256`。不使用模糊标题匹配或“读到某处”的停止条件。工具在写文件前验证所有选择，只导出选定内容及其中的图片，不复制全文，也不将选择配置中的自由文本 purpose 传给审阅者。公式以提取文本显示时会提示必须核对原始渲染；抽取材料不是排版验收。

第一轮审阅者只收到输出目录，先保存理解，再提供全文。选择是否公平仍由编辑者判断。已经读过全文的审阅者称为前部定位复核；生成了材料不代表已经完成盲读。
